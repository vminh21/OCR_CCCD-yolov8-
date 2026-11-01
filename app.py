try:
    import spaces
except ImportError:
    class MockSpaces:
        @staticmethod
        def GPU(*args, **kwargs):
            def decorator(fn):
                return fn
            return decorator
    spaces = MockSpaces()

import os
import sys
import types
from pathlib import Path

# Cấu hình thư mục ghi tạm cho Ultralytics YOLO
os.environ["YOLO_CONFIG_DIR"] = "/tmp"

# Polyfill pkg_resources cho gdown / VietOCR
try:
    import pkg_resources
except ImportError:
    pkg_res_mock = types.ModuleType("pkg_resources")
    class DummyDist:
        version = "5.2.0"
    pkg_res_mock.get_distribution = lambda name: DummyDist()
    sys.modules["pkg_resources"] = pkg_res_mock

# Patch Gradio Client schema parser bug on OpenAPI 3.1 boolean additionalProperties
try:
    import gradio_client.utils as client_utils
    orig_json_schema = client_utils._json_schema_to_python_type
    def safe_json_schema_to_python_type(schema, defs):
        if isinstance(schema, bool) or not isinstance(schema, dict):
            return "Any"
        return orig_json_schema(schema, defs)
    client_utils._json_schema_to_python_type = safe_json_schema_to_python_type
except Exception:
    pass

import gradio as gr
from fastapi.responses import HTMLResponse, FileResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from backend.main import app as fastapi_app, ROOT_DIR
from backend.core.pipeline import process_cccd

dist_path = ROOT_DIR / "frontend" / "dist"
dist_index = dist_path / "index.html"
template_index = ROOT_DIR / "frontend" / "templates" / "index.html"

def get_index_content():
    if dist_index.exists():
        return dist_index.read_text(encoding="utf-8")
    if template_index.exists():
        return template_index.read_text(encoding="utf-8")
    return "<h1>CCCD OCR API is running</h1>"

@spaces.GPU(duration=60)
def predict_gpu(image_path: str):
    """Hàm xử lý AI tăng tốc bằng GPU A10G cho Hugging Face Spaces"""
    if not image_path:
        return "Vui lòng nhập đường dẫn ảnh"
    try:
        import json
        res = process_cccd(image_path)
        return json.dumps(res, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"

# 1. Khởi tạo Gradio Blocks chứa hàm ZeroGPU @spaces.GPU để vượt qua bài kiểm tra ZeroGPU của Hugging Face
with gr.Blocks(title="CCCD OCR AI Engine") as demo:
    gr.Markdown("### CCCD OCR Backend Engine (NVIDIA A10G GPU)")
    inp = gr.Textbox(label="Đường dẫn ảnh kiểm tra")
    out = gr.Textbox(label="Kết quả trích xuất")
    btn = gr.Button("Trích xuất thông tin")
    btn.click(fn=predict_gpu, inputs=[inp], outputs=[out])

from gradio.routes import App

# 2. Hook App.create_app để đảm bảo demo.launch() giữ nguyên Facebook UI, assets và các endpoint API của FastAPI
orig_create_app = App.create_app

def custom_create_app(*args, **kwargs):
    server_app = orig_create_app(*args, **kwargs)
    
    # Route "/" phục vụ Facebook UI với headers no-cache (hỗ trợ cả GET và HEAD cho Gradio healthcheck)
    async def serve_facebook_home(request):
        if dist_index.exists():
            return FileResponse(
                dist_index,
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0"
                }
            )
        return HTMLResponse(get_index_content())

    # 1. Chèn "/" phục vụ Facebook UI ở vị trí đầu tiên
    server_app.routes.insert(0, Route("/", serve_facebook_home, methods=["GET", "HEAD"]))

    # 2. Chèn Mount "/assets" TRƯỚC route nội tại "/assets/{path:path}" của Gradio
    if (dist_path / "assets").exists():
        server_app.routes.insert(1, Mount("/assets", StaticFiles(directory=str(dist_path / "assets")), name="react_assets"))

    # 3. Chèn Mount "/media"
    Path("data/output").mkdir(parents=True, exist_ok=True)
    server_app.routes.insert(2, Mount("/media", StaticFiles(directory="data/output"), name="media_output"))

    # 4. Gắn toàn bộ router backend (/api, /predict, etc.) từ fastapi_app
    server_app.mount("/", fastapi_app)

    return server_app

App.create_app = custom_create_app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"[Startup] CCCD OCR Facebook UI Server launching on 0.0.0.0:{port}...")
    demo.launch(server_name="0.0.0.0", server_port=port, ssr_mode=False, show_api=False)


