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
try:
    from config.field_templates import AVATAR_COORDS
except ImportError:
    AVATAR_COORDS = None

from src.core.quality_check import check_quality
from src.detectors.card_detector import detect_and_crop_card
from src.core.enhancer import enhance_card
from src.detectors.field_detector import extract_fields_yolo, fix_card_orientation
from src.core.avatar_extractor import extract_avatar, save_avatar
from src.ocr.ocr_engine import read_all_fields
from src.core.validator import validate_results


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
        card_crop = fix_card_orientation(card_crop)
        # Lưu lại ảnh thẻ đã cắt
        cv2.imwrite(str(CARDS_DIR / f"{image_path.stem}_card.jpg"), card_crop)
    except ValueError:
        raise
    except Exception as e:
        print(f"❌ Dừng xử lý Stage 1: {e}")
        raise ValueError("Sai định dạng CCCD! Hệ thống chỉ hỗ trợ thẻ Căn cước công dân gắn chip chuẩn mới nhất.")

    # 4. ENHANCE IMAGE
    print("[3/7] Enhancing image...")
    enhanced = enhance_card(card_crop) # Biến ở đây tên là 'enhanced'
    cv2.imwrite(str(CARDS_DIR / f"{image_path.stem}_enhanced.jpg"), enhanced)

    # 5. STAGE 2: EXTRACT FIELDS (YOLO)
    print("[4/7] Extracting data...")
    field_images = extract_fields_yolo(enhanced)
    if not field_images or len(field_images) < 2 or ('so_cccd' not in field_images and 'ho_ten' not in field_images):
        raise ValueError("Sai định dạng CCCD! Hệ thống chỉ hỗ trợ thẻ Căn cước công dân gắn chip chuẩn mới nhất.")

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

    # 7.1 Kiểm tra xem có phải nội dung mặt sau thẻ CCCD
    all_raw_text = " ".join([str(v) for v in ocr_results.values()]).lower()
    back_keywords = ["đặc điểm", "nhân dạng", "ngón trỏ", "ngon tro", "cục cảnh sát", "giám đốc công an", "idvnm", "<<"]
    if any(kw in all_raw_text for kw in back_keywords):
        raise ValueError("Đây là mặt sau của CCCD. Chúng tôi chỉ trích xuất kết quả của mặt trước!")

    # 7.2 Kiểm tra chuẩn CCCD mới nhất (12 chữ số)
    so_cccd = final_data.get("so_cccd", "").strip()
    if not so_cccd or len(so_cccd) != 12:
        if so_cccd and len(so_cccd) == 9:
            raise ValueError("Sai định dạng CCCD! Ảnh tải lên là CMND 9 số cũ. Hệ thống chỉ hỗ trợ thẻ Căn cước công dân gắn chip chuẩn mới nhất (12 chữ số).")
        raise ValueError("Sai định dạng CCCD! Hệ thống chỉ hỗ trợ thẻ Căn cước công dân gắn chip chuẩn mới nhất (Số CCCD phải đủ 12 chữ số).")

    ho_ten = final_data.get("ho_ten", "").strip()
    if not ho_ten or len(ho_ten) < 2:
        raise ValueError("Sai định dạng CCCD! Không nhận diện được họ và tên hợp lệ của thẻ CCCD.")

    # 8. SAVE RESULTS
    print("[7/7] Saving results...")
    save_json(final_data, JSON_DIR / f"{image_path.stem}.json")
    save_text(final_data, TXT_DIR / f"{image_path.stem}.txt")
    print(f"✅ HOÀN TẤT: Kết quả lưu tại: {JSON_DIR} và {TXT_DIR}")

    return final_data