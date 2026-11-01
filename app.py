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
def predict_gpu(image_file):
    """Hàm xử lý AI tăng tốc bằng GPU A10G cho Hugging Face Spaces"""
    if not image_file:
        return {"error": "Vui lòng chọn ảnh"}
    try:
        return process_cccd(image_file)
    except Exception as e:
        return {"error": str(e)}

# 1. Khởi tạo Gradio Blocks chứa hàm ZeroGPU @spaces.GPU để vượt qua bài kiểm tra ZeroGPU của Hugging Face
with gr.Blocks(title="CCCD OCR AI Engine") as demo:
    gr.Markdown("### CCCD OCR Backend Engine (NVIDIA A10G GPU)")
    inp = gr.Image(label="Ảnh đầu vào", type="filepath")
    out = gr.JSON(label="Kết quả trích xuất")
    btn = gr.Button("Trích xuất thông tin")
    btn.click(fn=predict_gpu, inputs=[inp], outputs=[out])

# 2. Tinh chỉnh demo.app để chèn giao diện Facebook UI và static assets trước các route nội tại của Gradio
app = demo.app

# Route "/" phục vụ Facebook UI với headers no-cache
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

app.routes.insert(0, Route("/", serve_facebook_home, methods=["GET"]))

# Chèn Mount "/assets" và "/media" TRƯỚC route nội tại "/assets/{path:path}" của Gradio
if (dist_path / "assets").exists():
    app.routes.insert(1, Mount("/assets", StaticFiles(directory=str(dist_path / "assets")), name="react_assets"))

Path("data/output").mkdir(parents=True, exist_ok=True)
app.routes.insert(2, Mount("/media", StaticFiles(directory="data/output"), name="media_output"))

# Gắn toàn bộ router còn lại từ fastapi_app (/api, /predict, etc.)
app.mount("/", fastapi_app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"[Startup] CCCD OCR Facebook UI Server launching on 0.0.0.0:{port}...")
    demo.launch(server_name="0.0.0.0", server_port=port, ssr_mode=False)
