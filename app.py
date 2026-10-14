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
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.routing import Route
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

# 2. Truy cập ứng dụng FastAPI nội tại của Gradio
app = demo.app

# 3. Chèn Route trang chủ Facebook UI chuẩn vào đầu danh sách (ưu tiên khớp route / trước Gradio)
async def custom_facebook_home(request):
    return HTMLResponse(HTML_UI)

app.routes.insert(0, Route("/", custom_facebook_home, methods=["GET"]))

# 4. Mount thư mục tĩnh /media
Path("data/output").mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory="data/output"), name="media")

# 5. Tích hợp toàn bộ các API routes từ fastapi_app (Auth, Predict, History, Stats, Camera Probe)
existing_paths = {getattr(r, "path", None) for r in app.routes if getattr(r, "path", None)}
for route in fastapi_app.routes:
    path = getattr(route, "path", None)
    if path and path not in existing_paths:
        app.routes.append(route)
        existing_paths.add(path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"[Startup] CCCD OCR Facebook UI Server launching on 0.0.0.0:{port}...")
    demo.launch(server_name="0.0.0.0", server_port=port, ssr_mode=False)

