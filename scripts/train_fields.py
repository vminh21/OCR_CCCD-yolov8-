# scripts/train_fields.py
from ultralytics import YOLO

def main():
    # Sử dụng mô hình yolov8n.pt làm gốc để tinh chỉnh
    model = YOLO('yolov8n.pt')
    
    print("🚀 Bắt đầu huấn luyện YOLO Stage 2 - Nhận diện 8 trường dữ liệu...")
    
    # Huấn luyện mô hình
    model.train(
        data='data/detect_fields/data.yaml', # Trỏ tới file yaml mới tạo ở Bước 1
        epochs=100,                          # Cho học 100 vòng cho khôn
        imgsz=640,                           # Kích thước ảnh chuẩn của YOLO
        batch=16,                            # Có GPU MPS nên nâng lên batch 16 chạy cho tít
        device='mps',                        # Ép dùng GPU Apple Silicon, bái biệt CPU nóng ran!
        name='cccd_fields_v1'                # Tên thư mục lưu kết quả
    )
    
if __name__ == '__main__':
    main()