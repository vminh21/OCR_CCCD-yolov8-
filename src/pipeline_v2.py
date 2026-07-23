# src/pipeline_v2.py
import cv2
import json
from pathlib import Path

# Đảm bảo cấu trúc import khớp với thư mục của bạn
from config.settings import (
    CARDS_DIR,
    JSON_DIR,
    AVATARS_DIR,
    TXT_DIR
)
from config.field_templates import CCCD_FRONT_FIELDS
try:
    from config.field_templates import AVATAR_COORDS
except ImportError:
    AVATAR_COORDS = None

from src.quality_check import check_quality
from src.detector_yolo import detect_and_crop_card
from src.enhancer import enhance_card
from src.extractor_yolo import extract_fields_yolo
from src.extractor import extract_avatar, save_avatar
from src.ocr_engine import read_all_fields
from src.validator import validate_results


def save_json(data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_text(data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for k, v in data.items():
            f.write(f"{k}: {v}\n")


def process_cccd(image_path):
    """Process CCCD image using 2-stage pipeline: card detection + field extraction."""
    image_path = Path(image_path)
    print(f"\n{'='*60}\n🚀 PROCESSING: {image_path.name}\n{'='*60}")

    # 1. LOAD IMAGE
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"❌ Không thể đọc ảnh: {image_path}")
        return None

    # 2. QUALITY CHECK
    print("[1/7] Quality Check...")
    quality = check_quality(image)
    quality.summary()

    # 3. STAGE 1: DETECT & CROP CARD (YOLO)
    print("[2/7] Detecting & Cropping Card (YOLO)...")
    try:
        card_crop = detect_and_crop_card(image)
        # Lưu lại ảnh thẻ đã cắt
        cv2.imwrite(str(CARDS_DIR / f"{image_path.stem}_card.jpg"), card_crop)
    except Exception as e:
        # BẮT LỖI TẠI ĐÂY: Dừng hoàn toàn nếu không thấy thẻ hoặc up nhầm mặt sau
        print(f"❌ Dừng xử lý Stage 1: {e}")
        return None 

    # 4. ENHANCE IMAGE
    print("[3/7] Enhancing image...")
    enhanced = enhance_card(card_crop) # Biến ở đây tên là 'enhanced'
    cv2.imwrite(str(CARDS_DIR / f"{image_path.stem}_enhanced.jpg"), enhanced)

    # 5. STAGE 2: EXTRACT FIELDS (YOLO)
    print("[4/7] Extracting data...")
    # SỬA Ở ĐÂY: Truyền đúng biến 'enhanced' vào
    field_images = extract_fields_yolo(card_crop) 

    # Extract Avatar (if configured)
    if AVATAR_COORDS:
        try:
            avatar_img = extract_avatar(card_crop, AVATAR_COORDS)
            save_avatar(avatar_img, AVATARS_DIR / f"{image_path.stem}_avatar.jpg")
            print("   ✓ Avatar extracted")
        except Exception as e:
            print(f"   ⚠ Avatar extraction failed: {e}")

    # 6. STAGE 3: OCR READING
    print("[5/7] OCR reading...")
    # SỬA Ở ĐÂY: Truyền đúng biến 'field_images' vào hàm OCR
    ocr_results = read_all_fields(field_images)

    # 7. STAGE 4: VALIDATION
    print("[6/7] Validating data...")
    final_data = validate_results(ocr_results)

    # 8. SAVE RESULTS
    print("[7/7] Saving results...")
    save_json(final_data, JSON_DIR / f"{image_path.stem}.json")
    save_text(final_data, TXT_DIR / f"{image_path.stem}.txt")
    print(f"✅ HOÀN TẤT: Kết quả lưu tại {JSON_DIR.name}/ và {TXT_DIR.name}/")

    return final_data