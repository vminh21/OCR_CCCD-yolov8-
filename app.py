import os
import sys
import types

# Fix YOLO Ultralytics writable config dir
os.environ["YOLO_CONFIG_DIR"] = "/tmp"

# Polyfill pkg_resources for gdown (VietOCR) when setuptools is missing or pkg_resources is deprecated
try:
    import pkg_resources
except ImportError:
    pkg_res_mock = types.ModuleType("pkg_resources")
    class DummyDist:
        version = "5.2.0"
    pkg_res_mock.get_distribution = lambda name: DummyDist()
    sys.modules["pkg_resources"] = pkg_res_mock

import uvicorn
from main import app

try:
    import gradio as gr
    # Tạo một block Gradio nhỏ để tích hợp hoàn hảo với hệ thống kiểm tra của Hugging Face
    with gr.Blocks(title="CCCD OCR") as demo:
        gr.Markdown("### CCCD OCR System is Running via FastAPI Engine")
    
    # Mount Gradio vào route /_gradio, giữ nguyên route gốc "/" cho giao diện Facebook UI của bạn
    app = gr.mount_gradio_app(app, demo, path="/_gradio")
except Exception as e:
    print(f"[Notice] Gradio integration bypassed: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
