from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent / 'models' / 'yolov8_cccd_detect.pt'

_model = None

def _load_model():
    global _model
    if _model is None:
        if MODEL_PATH.exists():
            _model = YOLO(str(MODEL_PATH))
        else:
            print("⚠️ Không tìm thấy model tự train, đang dùng tạm yolov8n.pt...")
            # fallback: load pretrained yolov8n for quick tests
            _model = YOLO('yolov8n.pt')
    return _model

def detect_and_crop_card(image):
    """Detect CCCD bounding box and return cropped front card image.

    Args:
        image: numpy array (BGR) or image path string
    Returns:
        cropped image (numpy array) of detected FRONT card
    Raises:
        Exception if no card detected or if BACK card is detected
    """
    model = _load_model()

    # Support passing a path
    if isinstance(image, (str, Path)):
        img = cv2.imread(str(image))
        if img is None:
            raise ValueError(f"LỖI: Không thể đọc ảnh từ đường dẫn: {image}")
    else:
        img = image.copy()

    results = model(img, conf=0.45, iou=0.5, device='cpu')
    boxes = results[0].boxes if len(results) > 0 else None

    if boxes is None or len(boxes) == 0:
        raise Exception('Không tìm thấy thẻ CCCD nào trong ảnh')

    # TÌM MẶT TRƯỚC (Ưu tiên class_id == 1)
    front_card_box = None
    for b in boxes:
        class_id = int(b.cls[0])
        if class_id == 1:  # 1 là front-cccd
            front_card_box = b
            break
            
    # Báo lỗi nếu chỉ có class 0 (mặt sau)
    if front_card_box is None:
        raise Exception("Phát hiện mặt sau CCCD. Hệ thống chỉ xử lý mặt trước!")

    # Lấy tọa độ của mặt trước
    xyxy = front_card_box.xyxy[0].cpu().numpy() if hasattr(front_card_box.xyxy[0], 'cpu') else front_card_box.xyxy[0].numpy()
    x1, y1, x2, y2 = map(int, xyxy)

    # Safety clamp (Tránh tọa độ bị tràn ra ngoài kích thước thật của ảnh)
    h, w = img.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w - 1, x2), min(h - 1, y2)

    crop = img[y1:y2, x1:x2]
    return crop


if __name__ == '__main__':
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else None
    if not p:
        print('Usage: python src/detector_yolo.py <image_path>')
        sys.exit(1)
    try:
        img = detect_and_crop_card(p)
        out = Path(p).stem + '_front_card.png'
        cv2.imwrite(out, img)
        print('✅ Xong! Ảnh mặt trước đã lưu tại:', out)
    except Exception as e:
        print(f"❌ THẤT BẠI: {e}")