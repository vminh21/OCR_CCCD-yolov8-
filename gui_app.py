# gui_app.py
import os
import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from pathlib import Path

# Import pipeline và đường dẫn thư mục chuẩn từ hệ thống của bạn
from src.pipeline_v2 import process_cccd
from config.settings import CARDS_DIR

def open_image():
    """Hàm mở hộp thoại chọn ảnh và kích hoạt Pipeline AI"""
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
    if not file_path:
        return

    # 1. Cập nhật trạng thái giao diện đang load
    status_label.config(text="⏳ Đang xử lý AI (Stage 1 & Stage 2)...", fg="#d35400")
    root.update()

    try:
        # 2. Gọi hàm xử lý OCR từ hệ thống của bạn
        result_data = process_cccd(file_path)

        if not result_data:
            status_label.config(text="❌ Không tìm thấy CCCD hợp lệ!", fg="#c0392b")
            return

        # 3. Đổ dữ liệu text vào các nhãn bên cột phải
        lbl_id.config(text=result_data.get('so_cccd', '---'))
        lbl_name.config(text=result_data.get('ho_ten', '---'))
        lbl_dob.config(text=result_data.get('ngay_sinh', '---'))
        lbl_gender.config(text=result_data.get('gioi_tinh', '---'))
        lbl_nat.config(text=result_data.get('quoc_tich', '---'))
        lbl_origin.config(text=result_data.get('que_quan', '---'))
        lbl_residence.config(text=result_data.get('noi_ctru', '---'))
        lbl_expire.config(text=result_data.get('ngay_het_han', '---'))

        # 4. TÌM VÀ HIỂN THỊ ẢNH ĐÃ VẼ KHUNG (BOUNDING BOXES)
        # Đây là file mà extractor_yolo.py của bạn tự động ghi đè mỗi khi chạy
        viz_path = "output/cccd_fields_visualization.jpg"

        if os.path.exists(viz_path):
            show_image(viz_path)
        else:
            # Fallback nếu không tìm thấy
            show_image(file_path) 

        status_label.config(text="✅ Trích xuất thành công!", fg="#27ae60")

    except Exception as e:
        status_label.config(text=f"❌ Lỗi hệ thống: {e}", fg="#c0392b")

def show_image(img_path):
    """Hàm hiển thị ảnh OpenCV lên giao diện Tkinter"""
    img = cv2.imread(img_path)
    if img is None:
        return
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = rgb.shape[:2]
    max_w = 550 # Chiều rộng tối đa cho cột trái
    new_h = int(h * max_w / w)
    
    resized = cv2.resize(rgb, (max_w, new_h))
    img_pil = Image.fromarray(resized)
    imgtk = ImageTk.PhotoImage(image=img_pil)
    
    image_label.config(image=imgtk)
    image_label.image = imgtk # Giữ tham chiếu

# ==========================================
# KHỞI TẠO GIAO DIỆN TKINTER
# ==========================================
root = tk.Tk()
root.title("Hệ Thống AI Nhận Diện CCCD 2-Stage")
root.geometry("1100x650")
root.configure(bg="#2c3e50")
root.eval('tk::PlaceWindow . center')

# Container chính
main_frame = tk.Frame(root, bg="#2c3e50")
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Tiêu đề
title = tk.Label(main_frame, text="📸 HỆ THỐNG TRÍCH XUẤT THÔNG TIN CCCD", font=("Helvetica", 22, "bold"), bg="#2c3e50", fg="#ecf0f1")
title.pack(pady=(0, 20))

# Khung chứa nội dung (Chia 2 cột)
content_frame = tk.Frame(main_frame, bg="#2c3e50")
content_frame.pack(fill="both", expand=True)

# ===== CỘT TRÁI: HIỂN THỊ ẢNH =====
left_frame = tk.Frame(content_frame, bg="#ecf0f1", bd=2, relief="groove", width=600)
left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

btn_select = tk.Button(left_frame, text="📁 Chọn ảnh CCCD", font=("Helvetica", 14, "bold"), bg="#2980b9", fg="#000000", command=open_image)
btn_select.pack(pady=15)

# ĐÃ SỬA: Xóa bỏ width=50 và height=20 để tránh bị bóp ảnh thành 50x20 pixel
image_label = tk.Label(left_frame, bg="black", text="[Khu vực hiển thị ảnh]", fg="white", font=("Helvetica", 12))
image_label.pack(padx=15, pady=(0, 15), fill="both", expand=True)

status_label = tk.Label(left_frame, text="Sẵn sàng nhận ảnh...", font=("Helvetica", 12, "italic"), bg="#ecf0f1", fg="#7f8c8d")
status_label.pack(pady=5)

# ===== CỘT PHẢI: HIỂN THỊ THÔNG TIN =====
right_frame = tk.Frame(content_frame, bg="#ecf0f1", bd=2, relief="groove", width=450)
right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

info_title = tk.Label(right_frame, text="📋 KẾT QUẢ NHẬN DIỆN", font=("Helvetica", 16, "bold"), bg="#ecf0f1", fg="#2c3e50")
info_title.pack(pady=15)

# Hàm tạo layout cho từng trường thông tin
def create_field_row(parent, label_text):
    frame = tk.Frame(parent, bg="#ecf0f1")
    frame.pack(fill="x", padx=20, pady=8)
    lbl_title = tk.Label(frame, text=label_text, font=("Helvetica", 12, "bold"), bg="#ecf0f1", fg="#34495e", width=12, anchor="w")
    lbl_title.pack(side="left")
    lbl_value = tk.Label(frame, text="---", font=("Helvetica", 14), bg="#ecf0f1", fg="#27ae60", anchor="w")
    lbl_value.pack(side="left", fill="x", expand=True)
    return lbl_value

# Khởi tạo 8 nhãn chứa dữ liệu
lbl_id = create_field_row(right_frame, "Số CCCD:")
lbl_name = create_field_row(right_frame, "Họ tên:")
lbl_dob = create_field_row(right_frame, "Ngày sinh:")
lbl_gender = create_field_row(right_frame, "Giới tính:")
lbl_nat = create_field_row(right_frame, "Quốc tịch:")
lbl_origin = create_field_row(right_frame, "Quê quán:")
lbl_residence = create_field_row(right_frame, "Nơi cư trú:")
lbl_expire = create_field_row(right_frame, "Giá trị đến:")

root.mainloop()