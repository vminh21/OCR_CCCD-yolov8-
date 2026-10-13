import cv2
import os

from config.settings import (
    CARD_WIDTH,
    CARD_HEIGHT,
    OCR_OUT_DIR,
    AVATARS_DIR
)

from config.field_templates import (
    CCCD_FRONT_FIELDS
)

def field_to_pixels(field):
    """Chuyển đổi tỷ lệ % sang pixel và đảm bảo nằm trong phạm vi ảnh CCCD."""
    x_pct, y_pct, w_pct, h_pct = field

    x = int(x_pct * CARD_WIDTH)
    y = int(y_pct * CARD_HEIGHT)
    w = int(w_pct * CARD_WIDTH)
    h = int(h_pct * CARD_HEIGHT)

    #không vượt quá biên ảnh
    x = max(0, x)
    y = max(0, y)
    w = min(w, CARD_WIDTH - x)
    h = min(h, CARD_HEIGHT - y)

    return x, y, w, h

def crop_field(image, field):
    """Cắt vùng dữ liệu text/thông tin."""
    x, y, w, h = field_to_pixels(field)
    crop = image[y:y+h, x:x+w]
    
    # Trả về ảnh đen nhỏ nếu vùng cắt rỗng để tránh lỗi pipeline
    if crop.size == 0:
        return cv2.resize(image[:10, :10], (20, 20)) 
    return crop

def extract_avatar(image, avatar_coords):
    """Cắt vùng ảnh chân dung từ CCCD."""
    x, y, w, h = field_to_pixels(avatar_coords)
    return image[y:y+h, x:x+w]

def extract_fields(image):
    """Trích xuất tất cả các trường dữ liệu từ ảnh CCCD đã Warp."""
    if image.shape[1] != CARD_WIDTH or image.shape[0] != CARD_HEIGHT:
        image = cv2.resize(image, (CARD_WIDTH, CARD_HEIGHT))

    results = {}
    for field_name, coords in CCCD_FRONT_FIELDS.items():
        results[field_name] = crop_field(image, coords)
    return results

def save_field_images(field_images, filename_prefix="field"):
    """Lưu từng vùng dữ liệu đã cắt để kiểm tra OCR."""
    os.makedirs(OCR_OUT_DIR, exist_ok=True)
    for name, img in field_images.items():
        path = os.path.join(OCR_OUT_DIR, f"{filename_prefix}_{name}.png")
        cv2.imwrite(path, img)

def save_avatar(image, avatar_path):
    """Lưu ảnh chân dung vào thư mục chỉ định."""
    os.makedirs(AVATARS_DIR, exist_ok=True)
    cv2.imwrite(str(avatar_path), image)

def draw_field_boxes(image):
    """Vẽ khung bao quanh các vùng cần đọc để debug trực quan."""
    debug = image.copy()
    for field_name, coords in CCCD_FRONT_FIELDS.items():
        x, y, w, h = field_to_pixels(coords)
        
        # Vẽ hình chữ nhật
        cv2.rectangle(debug, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Ghi tên trường
        cv2.putText(
            debug, field_name, (x, y-5), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1
        )
    return debug