import cv2
import numpy as np

from dataclasses import dataclass
from typing import List

from config.settings import (
    BLUR_THRESHOLD,
    BRIGHTNESS_MIN,
    BRIGHTNESS_MAX
)

@dataclass
class QualityResult:
    is_ok: bool
    blur_score: float
    brightness: float
    width: int
    height: int
    warnings: List[str]

    def summary(self):

        print("\n========== QUALITY REPORT ==========")

        print(
            f"Blur Score : {self.blur_score:.2f}"
        )

        print(
            f"Brightness : {self.brightness:.2f}"
        )

        print(
            f"Resolution : {self.width} x {self.height}"
        )

        print(
            f"Status     : {'PASS' if self.is_ok else 'FAIL'}"
        )

        if self.warnings:

            print("\nWarnings:")

            for w in self.warnings:
                print(f" - {w}")

        print("====================================\n")


# BLUR CHECK
def calculate_blur_score(gray):

    """
    Laplacian Variance

    Cao -> nét
    Thấp -> mờ
    """

    lap = cv2.Laplacian(
        gray,
        cv2.CV_64F
    )

    return float(lap.var())


# BRIGHTNESS CHECK
def calculate_brightness(gray):

    """
    Mean intensity

    0   = đen
    255 = trắng
    """

    return float(np.mean(gray))


# MAIN QUALITY CHECK
def check_quality(
    image,
    min_size=480
):

    h, w = image.shape[:2]

    warnings = []

    # Gray
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Blur
    blur_score = calculate_blur_score(
        gray
    )

    if blur_score < BLUR_THRESHOLD:

        warnings.append(
            f"Ảnh bị mờ "
            f"(score={blur_score:.1f})"
        )

    # Brightness
    brightness = calculate_brightness(
        gray
    )

    if brightness < BRIGHTNESS_MIN:

        warnings.append(
            f"Ảnh quá tối "
            f"({brightness:.1f})"
        )

    if brightness > BRIGHTNESS_MAX:

        warnings.append(
            f"Ảnh quá sáng "
            f"({brightness:.1f})"
        )

    # Resolution
    if min(w, h) < min_size:

        warnings.append(
            f"Độ phân giải thấp "
            f"({w}x{h})"
        )

    # Final Decision
    is_ok = (
        blur_score >= BLUR_THRESHOLD
        and
        BRIGHTNESS_MIN <= brightness <= BRIGHTNESS_MAX
        and
        min(w, h) >= min_size
    )

    return QualityResult(
        is_ok=is_ok,
        blur_score=blur_score,
        brightness=brightness,
        width=w,
        height=h,
        warnings=warnings
    )