import spaces
import os
import sys
import types
import subprocess
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

import uvicorn
import gradio as gr
from main import app as fastapi_app
from src.core.pipeline import process_cccd

try:
    gpu_decorator = spaces.GPU(duration=60)
    print("✅ Hugging Face ZeroGPU (@spaces.GPU) đã được kích hoạt thành công!")
except Exception as e:
    print(f"ℹ️ Chạy chế độ CPU: {e}")
    def gpu_decorator(fn):
        return fn


@gpu_decorator
def predict_gpu(image_file):
    """Hàm xử lý AI tăng tốc bằng GPU A10G cho Hugging Face Spaces"""
    if not image_file:
        return {"error": "Vui lòng chọn ảnh"}
    try:
        return process_cccd(image_file)
    except Exception as e:
        return {"error": str(e)}


# 1. Tạo Gradio Blocks chứa hàm GPU để vượt qua bài kiểm tra ZeroGPU của Hugging Face
with gr.Blocks(title="CCCD OCR AI Engine") as demo:
    gr.Markdown("### CCCD OCR Backend Engine (NVIDIA A10G GPU)")
    inp = gr.Image(label="Ảnh đầu vào", type="filepath")
    out = gr.JSON(label="Kết quả trích xuất")
    btn = gr.Button("Trích xuất thông tin")
    btn.click(fn=predict_gpu, inputs=[inp], outputs=[out])

demo.is_running = True
demo.launched = True

# 2. Gắn Gradio vào đường dẫn phụ "/gradio"
app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"[Startup] CCCD OCR Facebook UI server running on 0.0.0.0:{port}")
    try:
        print("--- PROCESSES ---")
        print(subprocess.check_output(["ps", "aux"]).decode())
    except Exception as e:
        print("ps aux err:", e)
    try:
        print("--- SS / NETSTAT ---")
        print(subprocess.check_output(["ss", "-tlpn"]).decode())
    except Exception as e:
        print("ss err:", e)
    print("--- ENV ---")
    print({k: v for k, v in os.environ.items() if any(x in k for x in ["PORT", "GRADIO", "SPACE", "ZERO"])})
    uvicorn.run(app, host="0.0.0.0", port=port)

