import cv2
import easyocr
import pytesseract
import logging
import numpy as np

from config.settings import (
    OCR_LANG,
    OCR_USE_GPU,
    CONF_THRESHOLD,
    TESSERACT_CMD
)
from config.field_templates import FIELD_WHITELIST

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cấu hình Tesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# Khởi tạo EasyOCR Reader
try:
    reader = easyocr.Reader(OCR_LANG, gpu=OCR_USE_GPU)
except Exception as e:
    logger.error(f"Lỗi khởi tạo EasyOCR: {e}")
    reader = None

def prepare_image(image):
    """
    Tiền xử lý: Phóng to 2x để nhận diện nét rỗ hơn.
    EasyOCR hoạt động tốt hơn trên ảnh RGB hoặc Grayscale, không nên dùng Otsu.
    """
    # Phóng to giúp OCR nhìn rõ nét hơn
    enlarged = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return enlarged

def easyocr_read(image):
    """Thực hiện đọc text bằng EasyOCR với chế độ tin cậy cao."""
    if reader is None:
        return "", 0.0
    
    # paragraph=False để tránh ghép nhầm các dòng nếu ảnh bị nhiễu
    results = reader.readtext(image, detail=1, paragraph=False)
    
    if not results:
        return "", 0.0

    # Lấy text có độ tin cậy cao nhất
    texts = [item[1] for item in results]
    scores = [float(item[2]) for item in results]

    final_text = " ".join(texts)
    avg_conf = sum(scores) / len(scores) if scores else 0.0
    return final_text.strip(), avg_conf

def tesseract_read(image, whitelist=None):
    """Đọc bằng Tesseract với whitelist để ép kiểu ký tự (VD: chỉ số)."""
    # PSM 7: Coi ảnh là một dòng văn bản duy nhất (Phù hợp cho các trường CCCD)
    config = "--oem 3 --psm 7"
    
    if whitelist:
        config += f' -c tessedit_char_whitelist={whitelist}'

    try:
        text = pytesseract.image_to_string(image, lang="vie", config=config)
        return text.strip()
    except Exception as e:
        logger.error(f"Tesseract OCR error: {e}")
        return ""

def read_field(field_name, image):
    """Quy trình đọc từng trường thông tin."""
    processed_img = prepare_image(image)

    # Thử bằng EasyOCR
    text, conf = easyocr_read(processed_img)

    # Nếu độ tin cậy không đạt hoặc kết quả quá ngắn, fallback sang Tesseract
    if conf < CONF_THRESHOLD or len(text) < 2:
        whitelist = FIELD_WHITELIST.get(field_name)
        text = tesseract_read(processed_img, whitelist)
        return {
            "text": text,
            "confidence": conf,
            "engine": "tesseract"
        }

    return {
        "text": text,
        "confidence": conf,
        "engine": "easyocr"
    }

def read_all_fields(field_images):
    """Duyệt qua tất cả các trường đã cắt từ thẻ CCCD."""
    results = {}
    for field_name, image in field_images.items():
        results[field_name] = read_field(field_name, image)
    return results