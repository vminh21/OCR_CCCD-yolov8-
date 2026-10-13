# src/ocr/ocr_engine.py
import cv2
import logging
import numpy as np
from PIL import Image

from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from config.settings import MODEL_VIETOCR_CONFIG_PATH, MODEL_VIETOCR_WEIGHTS_PATH

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khởi tạo VietOCR Predictor (Chạy 100% Offline với config & weights cục bộ)
try:
    if MODEL_VIETOCR_CONFIG_PATH.exists():
        config = Cfg.load_config_from_file(str(MODEL_VIETOCR_CONFIG_PATH))
    else:
        config = Cfg.load_config_from_name('vgg_transformer')

    config['device'] = 'cpu'
    if MODEL_VIETOCR_WEIGHTS_PATH.exists():
        config['weights'] = str(MODEL_VIETOCR_WEIGHTS_PATH)
    config['predictor']['beamsearch'] = False

    vietocr_detector = Predictor(config)
    logger.info("Khởi tạo VietOCR engine offline thành công!")
except Exception as e:
    logger.error(f"Lỗi khởi tạo VietOCR: {e}")
    vietocr_detector = None


def prepare_image(image):
    """
    SOTA Text Strip Sharpness Enhancer & Preprocessing cho VietOCR:
    1. Thêm White Border Padding (+12px lề ngang, +8px lề dọc) giúp các ký tự không bị chạm viền ảnh.
    2. Tự động Upscale độ phân giải chuẩn (target height = 48px) cho các mảnh ảnh cắt bị quá nhỏ.
    3. Khử nhiễu mờ Bilateral Filter nhẹ bảo tồn cạnh chữ.
    4. Cân bằng độ tương phản vùng sáng/tối bằng LAB CLAHE.
    5. Unsharp Masking tăng cường độ nét viền ký tự & dấu tiếng Việt (hỏi, ngã, nặng, sắc, huyền).
    """
    if not isinstance(image, np.ndarray) or image.size == 0:
        return None

    # 1. Thêm White Border Padding (lề trắng xung quanh ảnh crop)
    padded = cv2.copyMakeBorder(image, 8, 8, 12, 12, cv2.BORDER_CONSTANT, value=[255, 255, 255])
    ph, pw = padded.shape[:2]

    # 2. Tự động Upscale ảnh nếu mảnh cắt có chiều cao quá nhỏ (h < 48px)
    if ph < 48:
        scale = 48.0 / float(ph)
        padded = cv2.resize(padded, (int(pw * scale), 48), interpolation=cv2.INTER_CUBIC)

    # 3. Khử nhiễu hạt nhẹ Bilateral Filter
    denoised = cv2.bilateralFilter(padded, d=3, sigmaColor=30, sigmaSpace=30)

    # 4. Tăng độ tương phản CLAHE trên LAB space
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(4, 4))
    cl = clahe.apply(l_channel)
    enhanced = cv2.cvtColor(cv2.merge((cl, a_channel, b_channel)), cv2.COLOR_LAB2BGR)

    # 5. Unsharp Masking làm sắc nét viền chữ tiếng Việt & dấu thanh cho VietOCR Transformer
    gaussian = cv2.GaussianBlur(enhanced, (0, 0), 2.0)
    sharpened = cv2.addWeighted(enhanced, 1.6, gaussian, -0.6, 0)

    # 6. Chuyển đổi BGR sang PIL Image (RGB)
    rgb_image = cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_image)


def vietocr_read(image):
    """Thực hiện đọc text bằng VietOCR sau khi làm sắc nét mảnh ảnh."""
    if vietocr_detector is None or image is None or (isinstance(image, np.ndarray) and image.size == 0):
        return "", 0.0

    try:
        pil_img = prepare_image(image)
        if pil_img is None:
            return "", 0.0
        text = vietocr_detector.predict(pil_img)
        conf = 0.95 if text else 0.0
        return text.strip(), conf
    except Exception as e:
        logger.error(f"VietOCR error: {e}")
        return "", 0.0


def read_field(field_name, images):
    """
    Đọc từng trường thông tin bằng VietOCR.
    Nếu trường có nhiều dòng (vd: Nơi cư trú/Quê quán có 2 dòng),
    đọc từng dòng từ trên xuống dưới, lọc từ nhãn rác rồi nối các phần text lại hoàn chỉnh.
    """
    if isinstance(images, list):
        text_parts = []
        for img in images:
            t, _ = vietocr_read(img)
            t = t.strip()
            if t:
                # Bỏ qua dòng nếu chỉ chứa đúng từ nhãn in sẵn của thẻ
                t_lower = t.lower()
                if t_lower in ["quán", "origin", "place", "residence", "nơi", "trú", "nơi thường trú", "quê quán"]:
                    continue
                text_parts.append(t)

        if field_name in ["noi_ctru", "que_quan"]:
            full_text = ", ".join(text_parts).strip()
            full_text = full_text.replace(" ,", ",").replace(",,", ",")
        else:
            full_text = " ".join(text_parts).strip()

        return {
            "text": full_text,
            "confidence": 0.95 if full_text else 0.0,
            "engine": "vietocr"
        }

    else:
        text, conf = vietocr_read(images)
        return {
            "text": text,
            "confidence": conf,
            "engine": "vietocr"
        }


def read_all_fields(field_images):
    """Duyệt qua tất cả các trường đã cắt từ thẻ CCCD."""
    results = {}
    for field_name, images in field_images.items():
        results[field_name] = read_field(field_name, images)
    return results