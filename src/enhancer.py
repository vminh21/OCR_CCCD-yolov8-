import cv2
import numpy as np

from config.settings import (
    CLAHE_CLIP_LIMIT,
    CLAHE_TILE_GRID,
    BILATERAL_D,
    BILATERAL_SIGMA_COLOR,
    BILATERAL_SIGMA_SPACE,
    ADAPTIVE_BLOCK_SIZE,
    ADAPTIVE_C
)

# BGR -> GRAY
def to_gray(image):

    return cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

# CLAHE
def apply_clahe(gray):

    clahe = cv2.createCLAHE(
        clipLimit=CLAHE_CLIP_LIMIT,
        tileGridSize=CLAHE_TILE_GRID
    )

    return clahe.apply(gray)

# DENOISE
def denoise(gray):

    return cv2.bilateralFilter(
        gray,
        d=BILATERAL_D,
        sigmaColor=BILATERAL_SIGMA_COLOR,
        sigmaSpace=BILATERAL_SIGMA_SPACE
    )


# THRESHOLD
def adaptive_threshold(gray):

    return cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        ADAPTIVE_BLOCK_SIZE,
        ADAPTIVE_C
    )

# MORPHOLOGY
def morphology_cleanup(binary):

    kernel = np.ones(
        (2, 2),
        dtype=np.uint8
    )

    opened = cv2.morphologyEx(
        binary,
        cv2.MORPH_OPEN,
        kernel,
        iterations=1
    )

    closed = cv2.morphologyEx(
        opened,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=1
    )

    return closed

# MAIN ENHANCER return ảnh nhị phân để tối ưu OCR
def enhance_card(image):
    gray = to_gray(image)
    contrast = apply_clahe(gray)
    smooth = denoise(contrast)
    binary = adaptive_threshold(smooth)
    clean = morphology_cleanup(binary)
    return clean