import cv2
import numpy as np
from config.settings import (
    CARD_WIDTH, CARD_HEIGHT,
    CARD_AREA_MIN_RATIO, CARD_AREA_MAX_RATIO
)

def order_points(pts):
    """Sắp xếp 4 điểm theo thứ tự: TL, TR, BR, BL"""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    
    width_a = np.linalg.norm(br - bl)
    width_b = np.linalg.norm(tr - tl)
    max_width = max(int(width_a), int(width_b))
    
    height_a = np.linalg.norm(tr - br)
    height_b = np.linalg.norm(tl - bl)
    max_height = max(int(height_a), int(height_b))

    # Ép khung hình nằm ngang
    if max_height > max_width:
        max_width, max_height = max_height, max_width
        dst = np.array([
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1],
            [0, 0]
        ], dtype="float32")
    else:
        dst = np.array([
            [0, 0], [max_width - 1, 0],
            [max_width - 1, max_height - 1], [0, max_height - 1]
        ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (max_width, max_height), flags=cv2.INTER_CUBIC)
    
    return cv2.resize(warped, (CARD_WIDTH, CARD_HEIGHT))

def find_card_contour(image):
    # Thêm padding để viền thẻ không chạm lề
    pad = 50
    padded = cv2.copyMakeBorder(image, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0,0,0))
    
    gray = cv2.cvtColor(padded, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 30, 200)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=3)

    contours, _ = cv2.findContours(closed, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    image_area = padded.shape[0] * padded.shape[1]

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 0.1 * image_area:
            continue

        peri = cv2.arcLength(contour, True)
        for eps in np.linspace(0.01, 0.1, 15):
            approx = cv2.approxPolyDP(contour, eps * peri, True)
            
            if len(approx) == 4 and cv2.isContourConvex(approx):
                pts = approx.reshape(4, 2)
                rect = cv2.minAreaRect(pts)
                (x, y), (w, h), angle = rect
                if w == 0 or h == 0: continue
                aspect = max(w, h) / min(w, h)
                
                # CCCD tỷ lệ ~ 1.58, lấy dư 1 khoảng dễ bắt
                if 1.25 <= aspect <= 2.2:
                    return pts - pad

    # Nếu không tìm thấy viền do ảnh chỉ toàn là CCCD
    h, w = image.shape[:2]
    aspect_img = max(w, h) / min(w, h)
    if 1.25 <= aspect_img <= 2.2:
        return np.array([
            [0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]
        ], dtype="float32")
        
    return None

def detect_and_warp(image):
    card_pts = find_card_contour(image)
    if card_pts is None:
        print("⚠ Không phát hiện được góc CCCD, thực hiện xoay ngang mặc định")
        h, w = image.shape[:2]
        if h > w:
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        return cv2.resize(image, (CARD_WIDTH, CARD_HEIGHT)), False

    warped = four_point_transform(image, card_pts)
    return warped, True