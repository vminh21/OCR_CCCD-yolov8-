# src/extractor_yolo.py
import os
import cv2
from ultralytics import YOLO
import logging

logger = logging.getLogger(__name__)

# Load mô hình YOLO phát hiện trường (Load 1 lần để tối ưu tốc độ)
try:
    field_model = YOLO("models/yolov8_fields.pt")
except Exception as e:
    logger.error(f"Không tìm thấy models/yolov8_fields.pt: {e}")
    field_model = None

# Ánh xạ từ Class Name của Roboflow sang Key hệ thống đang dùng
FIELD_MAP = {
    'current_place': 'noi_ctru',
    'dob': 'ngay_sinh',
    'expire_date': 'ngay_het_han',
    'gender': 'gioi_tinh',
    'id': 'so_cccd',
    'name': 'ho_ten',
    'nationality': 'quoc_tich',
    'origin_place': 'que_quan'
}

# Bản đồ màu sắc để vẽ lên giao diện GUI cho trực quan
COLOR_MAP = {
    'so_cccd': (0, 0, 255),       # Đỏ
    'ho_ten': (0, 255, 0),        # Xanh lá
    'ngay_sinh': (255, 0, 0),      # Xanh dương
    'gioi_tinh': (0, 255, 255),    # Vàng
    'quoc_tich': (255, 0, 255),    # Hồng
    'que_quan': (255, 255, 0),     # Cyan
    'noi_ctru': (0, 165, 255),     # Cam
    'ngay_het_han': (0, 0, 0)      # Đen
}

def extract_fields_yolo(card_image):
    """
    Dùng YOLO Stage 2 để tìm, cắt các trường thông tin trên thẻ CCCD
    và tự động xuất ảnh vẽ khung phục vụ hiển thị trên giao diện GUI.
    """
    if field_model is None:
        return {}

    # Chạy kết quả dự đoán trường dữ liệu
    results = field_model.predict(card_image, conf=0.5, verbose=False)
    
    field_crops = {}
    # Tạo một bản sao của ảnh thẻ để vẽ khung trực quan lên cột trái GUI
    img_visualize = card_image.copy()

    if len(results) > 0:
        boxes = results[0].boxes
        for box in boxes:
            # Lấy tọa độ bounding box của trường
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            x1, y1 = max(0, x1), max(0, y1)
            
            # Lấy tên trường định danh
            class_id = int(box.cls[0])
            class_name = field_model.names[class_id]
            vn_key = FIELD_MAP.get(class_name, class_name)
            
            # Cắt mảnh ảnh nhỏ lưu vào bộ nhớ để chuyển tiếp cho tầng OCR
            crop_img = card_image[y1:y2, x1:x2]
            if crop_img.size > 0:
                field_crops[vn_key] = crop_img
            
            # Vẽ hộp chữ nhật kèm nhãn text trực tiếp lên ảnh phục vụ GUI hiển thị
            color = COLOR_MAP.get(vn_key, (0, 255, 0))
            cv2.rectangle(img_visualize, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img_visualize, vn_key, (x1, max(y1 - 5, 15)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
        
    # Ghi đè file ảnh trực quan mới nhất vào thư mục đầu ra định sẵn
    os.makedirs("output", exist_ok=True)
    cv2.imwrite("output/cccd_fields_visualization.jpg", img_visualize)
            
    return field_crops