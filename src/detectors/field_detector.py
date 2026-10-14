# src/detectors/field_detector.py
import cv2
from ultralytics import YOLO
import logging

logger = logging.getLogger(__name__)

from config.settings import MODEL_STAGE2_PATH

try:
    field_model = YOLO(str(MODEL_STAGE2_PATH))
except Exception as e:
    logger.error(f"Không tìm thấy model tại {MODEL_STAGE2_PATH}: {e}")
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

# Bản đồ màu sắc để vẽ lên giao diện cho trực quan
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


def sort_multiline_crops(crop_items, field_name=""):
    """
    Thuật toán Sắp Xếp Dòng & Cột Thông Minh:
    1. Tính trọng tâm trục Y: cy = (y1 + y2) / 2.
    2. Đối với Nơi thường trú (noi_ctru): Dòng 1 (Thôn/Xóm/Tổ/Số nhà) nằm sau nhãn nên thụt lề phải (x1 lớn),
       Dòng 2 (Xã/Huyện/Tỉnh) bắt đầu từ lề trái (x1 nhỏ).
    3. Nhóm các ô chữ theo dòng, sắp xếp từ Trái -> Phải (x1), Dòng 1 trước -> Dòng 2 sau.
    """
    if not crop_items:
        return []
    if len(crop_items) == 1:
        return [crop_items[0][4]]

    # Sắp xếp thô theo trọng tâm cy
    sorted_by_cy = sorted(crop_items, key=lambda it: (it[0] + it[2]) / 2.0)

    # Nếu có 2 box (trường hợp phổ biến nhất của Nơi thường trú)
    if len(crop_items) == 2 and field_name == "noi_ctru":
        b0, b1 = crop_items[0], crop_items[1]
        cy0 = (b0[0] + b0[2]) / 2.0
        cy1 = (b1[0] + b1[2]) / 2.0
        # Nếu box 0 có x1 lớn (nằm sau nhãn) và box 1 có x1 nhỏ (dòng 2 từ lề trái)
        # hoặc cy0 < cy1: Box 0 là Dòng 1, Box 1 là Dòng 2
        if b0[1] > b1[1] and cy0 <= cy1 + 15:
            return [b0[4], b1[4]]
        elif b1[1] > b0[1] and cy1 <= cy0 + 15:
            return [b1[4], b0[4]]

    # Trường hợp chung: gom nhóm theo min_cy
    min_cy = min((it[0] + it[2]) / 2.0 for it in crop_items)
    line1 = [it for it in crop_items if (it[0] + it[2]) / 2.0 < min_cy + 18]
    line2 = [it for it in crop_items if (it[0] + it[2]) / 2.0 >= min_cy + 18]

    line1_sorted = sorted(line1, key=lambda it: it[1])  # sort theo x1
    line2_sorted = sorted(line2, key=lambda it: it[1])  # sort theo x1

    return [it[4] for it in line1_sorted] + [it[4] for it in line2_sorted]


def safe_field_predict(model, img, **kwargs):
    try:
        return model.predict(img, **kwargs)
    except Exception:
        kw = dict(kwargs)
        kw["device"] = "cpu"
        return model.predict(img, **kw)


def fix_card_orientation(card_img):
    """
    Kiểm tra và tự động xoay thẻ 180° nếu thẻ bị lộn ngược.
    Sử dụng field_model đánh giá số lượng và độ tin cậy của các trường thông tin.
    """
    if field_model is None or card_img is None:
        return card_img

    # Đánh giá hướng 0°
    res0 = safe_field_predict(field_model, card_img, conf=0.30, verbose=False)
    score0 = sum(float(b.conf[0]) for b in res0[0].boxes) if len(res0) > 0 else 0
    count0 = len(res0[0].boxes) if len(res0) > 0 else 0

    # Đánh giá hướng 180°
    card_180 = cv2.rotate(card_img, cv2.ROTATE_180)
    res180 = safe_field_predict(field_model, card_180, conf=0.30, verbose=False)
    score180 = sum(float(b.conf[0]) for b in res180[0].boxes) if len(res180) > 0 else 0
    count180 = len(res180[0].boxes) if len(res180) > 0 else 0

    if score180 > score0 or count180 > count0 + 2:
        logger.info("Phát hiện thẻ bị ngược 180°, tự động xoay đúng chiều!")
        return card_180

    return card_img


def extract_fields_yolo(card_image):
    """
    Dùng YOLO Stage 2 để tìm, cắt các trường thông tin trên thẻ CCCD.
    Hỗ trợ xử lý trường nhiều dòng (như Nơi cư trú/Quê quán 2 dòng):
    - Tự động gom nhóm các khung detection cùng loại.
    - Áp dụng thuật toán sắp xếp Dòng 1 -> Dòng 2 và Trái -> Phải (x1).
    """
    if field_model is None:
        return {}

    # Chạy kết quả dự đoán trường dữ liệu
    results = safe_field_predict(field_model, card_image, conf=0.45, verbose=False)


    raw_crops = {}
    img_visualize = card_image.copy()

    if len(results) > 0:
        boxes = results[0].boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            x1, y1 = max(0, x1), max(0, y1)

            class_id = int(box.cls[0])
            class_name = field_model.names[class_id]
            vn_key = FIELD_MAP.get(class_name, class_name)

            # Nếu là Dòng 1 của Nơi thường trú (x1 > 420 sau nhãn), thụt mép trên 2px để tránh dính mực in dòng Quê quán
            if vn_key == 'noi_ctru' and x1 > 420:
                y1_crop = min(y2 - 10, y1 + 2)
            else:
                y1_crop = y1

            crop_img = card_image[y1_crop:y2, x1:x2]
            if crop_img.size > 0:
                if vn_key not in raw_crops:
                    raw_crops[vn_key] = []
                raw_crops[vn_key].append((y1, x1, y2, x2, crop_img))

            color = COLOR_MAP.get(vn_key, (0, 255, 0))
            cv2.rectangle(img_visualize, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img_visualize, vn_key, (x1, max(y1 - 5, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

    from config.settings import OUTPUT_DIR
    viz_path = OUTPUT_DIR / "cccd_fields_visualization.jpg"
    cv2.imwrite(str(viz_path), img_visualize)

    # Sắp xếp theo thuật toán Dòng 1 -> Dòng 2 & Trái -> Phải (x1)
    field_crops = {}
    for key, items in raw_crops.items():
        field_crops[key] = sort_multiline_crops(items, field_name=key)

    return field_crops