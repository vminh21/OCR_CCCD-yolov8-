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

# Hotfix tương thích Gradio với schema Pydantic v2
try:
    import gradio_client.utils as client_utils
    _orig_json_schema = client_utils._json_schema_to_python_type
    def _safe_json_schema(schema, defs=None):
        if isinstance(schema, bool):
            return "typing.Any"
        return _orig_json_schema(schema, defs)
    client_utils._json_schema_to_python_type = _safe_json_schema
except Exception as e:
    pass

import gradio as gr
from gradio.routes import App
from starlette.routing import Route
from fastapi.responses import HTMLResponse
from main import app as fastapi_app, HTML_UI
from src.core.pipeline import process_cccd


@spaces.GPU(duration=60)
def predict_gpu(image_file):
    """Hàm xử lý AI tăng tốc bằng GPU A10G cho Hugging Face Spaces"""
    if not image_file:
        return {"error": "Vui lòng chọn ảnh"}
    try:
        return process_cccd(image_file)
    except Exception as e:
        return {"error": str(e)}


# 1. Khởi tạo Gradio Blocks chứa hàm ZeroGPU @spaces.GPU
with gr.Blocks(title="CCCD OCR AI Engine") as demo:
    gr.Markdown("### CCCD OCR Backend Engine (NVIDIA A10G GPU)")
    inp = gr.Image(label="Ảnh đầu vào", type="filepath")
    out = gr.JSON(label="Kết quả trích xuất")
    btn = gr.Button("Trích xuất thông tin")
    btn.click(fn=predict_gpu, inputs=[inp], outputs=[out])

# 2. Hook App.create_app để chèn 100% Giao diện Facebook UI vào trang chủ "/" và mount toàn bộ API
orig_create_app = App.create_app

@staticmethod
def patched_create_app(blocks, app_kwargs=None, auth_dependency=None):
    app = orig_create_app(blocks, app_kwargs, auth_dependency)
    # Giao diện Facebook UI luôn được ưu tiên khớp đầu tiên tại trang chủ "/"
    app.routes.insert(0, Route("/", lambda req: HTMLResponse(HTML_UI), methods=["GET"]))
    # Gắn toàn bộ router và static media từ fastapi_app
    app.mount("/", fastapi_app)
    return app

App.create_app = patched_create_app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"[Startup] CCCD OCR Facebook UI Server launching on 0.0.0.0:{port}...")
    demo.launch(server_name="0.0.0.0", server_port=port, ssr_mode=False)
