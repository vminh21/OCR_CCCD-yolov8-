# src/core/enhancer.py
import cv2
import numpy as np


def enhance_card(image: np.ndarray) -> np.ndarray:
    """
    SOTA Image Enhancement & Adaptive Deblurring Pipeline:
    1. Bilateral Denoising: Lọc triệt để nhiễu mờ/nhiễu hạt camera mà không làm mờ viền chữ.
    2. Đo độ mờ ảnh (Blur Metric via Variance of Laplacian).
    3. Tự động kích hoạt Dynamic CLAHE để cân bằng ánh sáng và phục hồi độ tương phản vùng chữ.
    4. Multi-Scale Unsharp Masking & Laplacian Sharpening: Tái tạo các nét chữ mảnh, dấu tiếng Việt
       sau khi nắn phẳng phối cảnh từ góc nghiêng 45°-60°.
    """
    if image is None or image.size == 0:
        return image

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Dynamic CLAHE Clip Limit dựa trên mức độ mờ của ảnh
    clip_limit = 3.5 if blur_score < 120.0 else 2.2

    # 1. Bilateral Denoising: Khử nhiễu nhưng bảo toàn cạnh ký tự
    denoised = cv2.bilateralFilter(image, d=5, sigmaColor=60, sigmaSpace=60)

    # 2. Chuyển sang hệ màu LAB để cân bằng ánh sáng qua CLAHE trên kênh L
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)

    limg = cv2.merge((cl, a_channel, b_channel))
    enhanced_bgr = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    # 3. Dynamic Multi-Scale Deblurring & High-Pass Sharpening
    if blur_score < 120.0:
        # Ma trận Kernel Laplacian khử mờ chuyên sâu cho nét chữ bị nhòe / kéo dãn
        laplacian_kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ], dtype=np.float32)
        deblurred = cv2.filter2D(enhanced_bgr, -1, laplacian_kernel)
        gaussian = cv2.GaussianBlur(deblurred, (0, 0), 2.0)
        sharpened = cv2.addWeighted(deblurred, 1.6, gaussian, -0.6, 0)
    else:
        # Làm nét nhẹ nhàng cho ảnh đủ sáng và nét, tránh tạo viền halo quanh chữ
        gaussian = cv2.GaussianBlur(enhanced_bgr, (0, 0), 2.5)
        sharpened = cv2.addWeighted(enhanced_bgr, 1.45, gaussian, -0.45, 0)

    return sharpened