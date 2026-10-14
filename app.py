# ==============================================================
# app.py — Giao diện AI CCCD OCR Chuẩn Hugging Face ZeroGPU
# ==============================================================
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
from config.settings import CARDS_DIR, AVATARS_DIR
from src.core.pipeline import process_cccd

# Tích hợp ZeroGPU Decorator (Chạy trên GPU A10G khi deploy trên Hugging Face)
try:
    import spaces
    gpu_decorator = spaces.GPU(duration=60)
    print("✅ Hugging Face ZeroGPU (@spaces.GPU) đã được kích hoạt thành công!")
except Exception as e:
    print(f"ℹ️ Chạy chế độ CPU cục bộ: {e}")
    def gpu_decorator(fn):
        return fn


@gpu_decorator
def predict_cccd(image_file):
    if not image_file:
        return None, None, {"thong_bao": "Vui lòng tải lên ảnh CCCD hoặc chụp từ camera."}, []
    
    try:
        data = process_cccd(image_file)
        if not data:
            return None, None, {"loi": "Không nhận diện được thẻ CCCD hợp lệ."}, []
        
        stem = Path(image_file).stem
        card_img_path = str(CARDS_DIR / f"{stem}_card.jpg")
        avatar_img_path = str(AVATARS_DIR / f"{stem}_avatar.jpg")
        
        card_res = card_img_path if Path(card_img_path).exists() else None
        avatar_res = avatar_img_path if Path(avatar_img_path).exists() else None
        
        field_labels = {
            "so_cccd": "Số CCCD",
            "ho_ten": "Họ và Tên",
            "ngay_sinh": "Ngày Sinh",
            "gioi_tinh": "Giới Tính",
            "quoc_tich": "Quốc Tịch",
            "que_quan": "Quê Quán",
            "noi_thuong_tru": "Nơi Thường Trú",
            "gia_tri_den": "Có Giá Trị Đến"
        }
        
        table_data = []
        for key, label in field_labels.items():
            if key in data:
                table_data.append([label, str(data[key])])
        
        for key, val in data.items():
            if key not in field_labels:
                table_data.append([key, str(val)])
                
        return card_res, avatar_res, data, table_data

    except Exception as e:
        err_msg = str(e)
        return None, None, {"loi": err_msg}, [["Lỗi", err_msg]]


# Xây dựng giao diện tương tác Gradio
with gr.Blocks(title="CCCD OCR — Hệ Thống Nhận Diện Căn Cước Công Dân") as demo:
    gr.Markdown("""
    # 🪪 CCCD OCR — Nhận Diện & Trích Xuất Thẻ Căn Cước Công Dân Việt Nam
    **Hệ thống AI xử lý 2 giai đoạn YOLOv8 + VietOCR Transformer — Tăng tốc bởi NVIDIA A10G (ZeroGPU)**
    """)

    with gr.Row():
        with gr.Column(scale=1):
            input_image = gr.Image(
                label="Tải Ảnh Hoặc Chụp Trực Tiếp Từ Camera",
                type="filepath",
                sources=["upload", "webcam"]
            )
            btn_submit = gr.Button("🔍 Nhận Diện & Trích Xuất CCCD", variant="primary", size="lg")
            gr.Markdown("""
            *Hướng dẫn*:
            - Sử dụng ảnh **Mặt trước** của thẻ Căn cước công dân gắn chip mới nhất (12 chữ số).
            - Chụp rõ nét, đủ ánh sáng, không bị che khuất 4 góc thẻ.
            """)

        with gr.Column(scale=1):
            with gr.Row():
                output_card = gr.Image(label="Ảnh Thẻ Nắn Thẳng (Stage 1)")
                output_avatar = gr.Image(label="Ảnh Chân Dung (Avatar)")
            
            output_table = gr.Dataframe(
                headers=["Trường Dữ Liệu", "Giá Trị Nhận Diện"],
                label="Kết Quả Bóc Tách Chi Tiết",
                interactive=False
            )
            output_json = gr.JSON(label="Dữ Liệu JSON Chuẩn Hóa")

    btn_submit.click(
        fn=predict_cccd,
        inputs=[input_image],
        outputs=[output_card, output_avatar, output_json, output_table]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
