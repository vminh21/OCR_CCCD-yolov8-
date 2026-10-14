import os
os.environ["YOLO_CONFIG_DIR"] = "/tmp/Ultralytics"
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
