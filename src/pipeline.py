import cv2
import json
from pathlib import Path

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
from src.detector import detect_and_warp
from src.enhancer import enhance_card
from src.extractor import extract_fields, extract_avatar, save_avatar
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
    image_path = Path(image_path)
    print(f"\n{'='*60}\n🚀 PROCESSING: {image_path.name}\n{'='*60}")

    # 1. LOAD IMAGE
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Không thể đọc ảnh: {image_path}")
        return None

    # 2. QUALITY CHECK
    print("[1/7] Quality Check...")
    quality = check_quality(image)
    quality.summary()

    # 3. DETECT & WARP
    print("[2/7] Detecting & Warping...")
    warped, found = detect_and_warp(image)
    cv2.imwrite(str(CARDS_DIR / f"{image_path.stem}_card.jpg"), warped)
    
    # 4. ENHANCE IMAGE
    print("[3/7] Enhancing image...")
    enhanced = enhance_card(warped)
    cv2.imwrite(str(CARDS_DIR / f"{image_path.stem}_enhanced.jpg"), enhanced)

    # 5. EXTRACT FIELDS & AVATAR
    print("[4/7] Extracting data...")
    fields = extract_fields(enhanced)
    
    # Xử lý Avatar (nếu đã cấu hình tọa độ trong template)
    if AVATAR_COORDS:
        avatar_img = extract_avatar(warped, AVATAR_COORDS)
        save_avatar(avatar_img, AVATARS_DIR / f"{image_path.stem}_avatar.jpg")
        print("   ✓ Avatar extracted")

    # 6. OCR
    print("[5/7] OCR reading...")
    ocr_results = read_all_fields(fields)

    # 7. VALIDATION
    print("[6/7] Validating data...")
    final_data = validate_results(ocr_results)

    # 8. SAVE RESULT
    print("[7/7] Saving results...")
    save_json(final_data, JSON_DIR / f"{image_path.stem}.json")
    save_text(final_data, TXT_DIR / f"{image_path.stem}.txt")

    # FINAL REPORT
    print(f"\n{'='*60}\nKẾT QUẢ OCR\n{'='*60}")
    for k, v in final_data.items():
        print(f"{k:15s}: {v}")
    print('=' * 60)

    return final_data