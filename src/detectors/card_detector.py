# src/detectors/card_detector.py
from ultralytics import YOLO
import cv2
import numpy as np
import math
from pathlib import Path

from config.settings import MODEL_STAGE1_PATH, CARD_WIDTH, CARD_HEIGHT
MODEL_PATH = MODEL_STAGE1_PATH

_model = None


def _load_model():
    global _model
    if _model is None:
        if MODEL_PATH.exists():
            _model = YOLO(str(MODEL_PATH))
        else:
            print("⚠️ Không tìm thấy model tự train, đang dùng tạm yolov8n.pt...")
            _model = YOLO('yolov8n.pt')
    return _model


def rotate_bound(image, angle):
    """Xoay ảnh theo góc bất kỳ mà không bị cắt mất góc viền ngoài."""
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # Tính kích thước mới của ảnh sau khi xoay để chứa toàn bộ hình
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # Điều chỉnh ma trận tịnh tiến
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    return cv2.warpAffine(image, M, (nW, nH), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def order_points(pts):
    """
    Sắp xếp 4 điểm góc cực kỳ chuẩn xác (Polar & Geometric Angle Ordering):
    Thứ tự trả về: [Top-Left, Top-Right, Bottom-Right, Bottom-Left].
    Xử lý hoàn hảo trường hợp thẻ bị nghiêng 45° - 60° (hình thoi) không bị đảo đỉnh.
    """
    pts = np.array(pts, dtype="float32")
    center = np.mean(pts, axis=0)

    # 1. Tính góc cực từ tâm đến mỗi đỉnh và sắp xếp theo chiều kim đồng hồ
    angles = np.arctan2(pts[:, 1] - center[1], pts[:, 0] - center[0])
    sort_idx = np.argsort(angles)
    pts_sorted = pts[sort_idx]

    # 2. Xác định cạnh dài (Chiều ngang thẻ) vs cạnh ngắn (Chiều dọc thẻ)
    l0 = np.linalg.norm(pts_sorted[1] - pts_sorted[0])
    l1 = np.linalg.norm(pts_sorted[2] - pts_sorted[1])
    l2 = np.linalg.norm(pts_sorted[3] - pts_sorted[2])
    l3 = np.linalg.norm(pts_sorted[0] - pts_sorted[3])

    avg_w = (l0 + l2) / 2.0
    avg_h = (l1 + l3) / 2.0

    # Thẻ CCCD luôn có Chiều ngang (Width ~860) > Chiều dọc (Height ~542)
    # Nếu cạnh 0-1 là cạnh ngắn, dịch chuyển 1 nấc để cạnh 0-1 là cạnh dài
    if avg_w < avg_h:
        pts_sorted = np.roll(pts_sorted, -1, axis=0)

    # 3. Xác định cạnh dài nào ở trên (Top Edge) vs ở dưới (Bottom Edge)
    top_edge_y = (pts_sorted[0][1] + pts_sorted[1][1]) / 2.0
    bottom_edge_y = (pts_sorted[2][1] + pts_sorted[3][1]) / 2.0

    if top_edge_y > bottom_edge_y:
        pts_sorted = np.roll(pts_sorted, -2, axis=0)

    # 4. Trong cạnh TRÊN (pts_sorted[0] và pts_sorted[1]), điểm có X nhỏ hơn là Top-Left
    if pts_sorted[0][0] > pts_sorted[1][0]:
        p_tl = pts_sorted[1]
        p_tr = pts_sorted[0]
        p_br = pts_sorted[3]
        p_bl = pts_sorted[2]
    else:
        p_tl = pts_sorted[0]
        p_tr = pts_sorted[1]
        p_br = pts_sorted[2]
        p_bl = pts_sorted[3]

    return np.array([p_tl, p_tr, p_br, p_bl], dtype="float32")


def calculate_missing_fourth_corner(pts3):
    """
    Dựa trên tính chất đối xứng hình bình hành / hình chữ nhật của thẻ CCCD.
    Cho 3 điểm góc [P1, P2, P3], tự động tính điểm góc thứ 4 bị che khuất:
    P_thiếu = 2 * Midpoint - P_đối_diện
    """
    pts = np.array(pts3, dtype="float32")
    dists = [np.linalg.norm(pts[i] - pts[j]) for i in range(3) for j in range(i + 1, 3)]
    max_idx = np.argmax(dists)

    pairs = [(0, 1), (0, 2), (1, 2)]
    p_diag1, p_diag2 = pairs[max_idx]
    p_other = 3 - p_diag1 - p_diag2

    midpoint = (pts[p_diag1] + pts[p_diag2]) / 2.0
    p_missing = 2.0 * midpoint - pts[p_other]

    pts4 = np.zeros((4, 2), dtype="float32")
    pts4[0] = pts[0]
    pts4[1] = pts[1]
    pts4[2] = pts[2]
    pts4[3] = p_missing
    return pts4


def align_and_warp_card(image_crop):
    """
    Perspective Transform & Deskew SOTA cho mọi góc nghiêng (0°, 5°, 15°, 30°, 45°...):
    1. Phân đoạn thẻ CCCD khỏi nền (bàn tối / bàn sáng) qua Otsu Thresholding + Morphological Closing.
    2. Tìm chính xác đường bao lớn nhất của thẻ (diện tích > 40% crop).
    3. Áp dụng minAreaRect để tính 4 góc thẻ thực tế.
    4. Sắp xếp thứ tự 4 góc (TL, TR, BR, BL) và nắn phẳng chuẩn xác về 860x542 px qua Perspective Transform.
    5. Fallback: Canny + approxPolyDP nếu threshold không khớp.
    """
    h, w = image_crop.shape[:2]
    target_w, target_h = CARD_WIDTH, CARD_HEIGHT

    gray = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)

    best_cnt = None
    best_diff = 999.0

    # 1. Thử phân đoạn nhị phân tách thẻ khỏi nền (cả nền tối lẫn nền sáng)
    for thresh_type in [cv2.THRESH_BINARY, cv2.THRESH_BINARY_INV]:
        _, thresh = cv2.threshold(gray, 0, 255, thresh_type + cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            area = cv2.contourArea(c)
            # Thẻ CCCD chiếm từ 35% đến 96% diện tích crop (loại trừ contour 100% bao toàn khung ảnh)
            if 0.35 * (w * h) <= area <= 0.96 * (w * h):
                rect = cv2.minAreaRect(c)
                rw, rh = rect[1]
                if rw > 0 and rh > 0:
                    ar = max(rw, rh) / min(rw, rh)
                    # Tỷ lệ thẻ CCCD chuẩn ~ 1.58
                    if 1.2 <= ar <= 2.2:
                        diff = abs(ar - 1.58)
                        if diff < best_diff:
                            best_diff = diff
                            best_cnt = c

    # 2. Nếu tìm được đường bao toàn vẹn của thẻ qua threshold
    if best_cnt is not None:
        rect = cv2.minAreaRect(best_cnt)
        box = cv2.boxPoints(rect)
        pts = order_points(box.astype("float32"))
        dst = np.float32([
            [0, 0],
            [target_w - 1, 0],
            [target_w - 1, target_h - 1],
            [0, target_h - 1]
        ])
        M = cv2.getPerspectiveTransform(pts, dst)
        warped = cv2.warpPerspective(image_crop, M, (target_w, target_h), flags=cv2.INTER_LANCZOS4)
        return warped


    # 3. Fallback: Dùng Canny + Contour
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 40, 140)
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4 and cv2.contourArea(c) > 0.20 * (w * h):
            pts = order_points(approx.reshape(4, 2).astype("float32"))
            dst = np.float32([
                [0, 0],
                [target_w - 1, 0],
                [target_w - 1, target_h - 1],
                [0, target_h - 1]
            ])
            M = cv2.getPerspectiveTransform(pts, dst)
            return cv2.warpPerspective(image_crop, M, (target_w, target_h), flags=cv2.INTER_LANCZOS4)
        elif len(approx) == 3 and cv2.contourArea(c) > 0.15 * (w * h):
            card_contour = calculate_missing_fourth_corner(approx.reshape(3, 2))
            pts = order_points(card_contour.astype("float32"))
            dst = np.float32([
                [0, 0],
                [target_w - 1, 0],
                [target_w - 1, target_h - 1],
                [0, target_h - 1]
            ])
            M = cv2.getPerspectiveTransform(pts, dst)
            return cv2.warpPerspective(image_crop, M, (target_w, target_h), flags=cv2.INTER_LANCZOS4)

    return cv2.resize(image_crop, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)



def calculate_alignment_score(box):
    """Tính điểm chất lượng góc xoay kết hợp giữa Confidence và Aspect Ratio của CCCD (~1.58)."""
    conf = float(box.conf[0])
    xyxy = box.xyxy[0].cpu().numpy() if hasattr(box.xyxy[0], 'cpu') else box.xyxy[0].numpy()
    bw = xyxy[2] - xyxy[0]
    bh = xyxy[3] - xyxy[1]
    ar = bw / max(1.0, bh)
    ar_score = math.exp(-((ar - 1.58) ** 2) / 0.15) if ar >= 1.1 else 0.1
    return conf * ar_score


def detect_and_crop_card(image):
    """
    TỰ ĐỘNG PHÁT HIỆN & CẮT NẮN THẺ CCCD Ở MỌI GÓC NGHIÊNG (0°, 30°, 45°, 60°, 90°, 180°, 270°...):
    - Đánh giá theo chiến lược Aspect-Ratio & Confidence Alignment:
      + Bước 1: Thử góc 0°. Nếu ảnh thẳng nằm ngang (Score >= 0.88), xuất kết quả ngay (~0.05s).
      + Bước 2: Thử các góc trực giao 90°, 180°, 270°. Nếu đạt Score >= 0.88, xử lý ngay.
      + Bước 3: Nếu ảnh bị chụp nghiêng chéo (30°, 45°, 60°...), quét toàn bộ các góc nghiêng trung gian.
    - Trích xuất b-box front-cccd chuẩn xác nhất và nắn thẳng về tỷ lệ 860x542.
    """
    model = _load_model()

    if isinstance(image, (str, Path)):
        img = cv2.imread(str(image))
        if img is None:
            raise ValueError(f"LỖI: Không thể đọc ảnh từ đường dẫn: {image}")
    else:
        img = image.copy()

    best_front_score = -1.0
    best_front_box = None
    best_front_img = img

    best_back_score = -1.0
    best_back_box = None

    def evaluate_boxes(boxes, current_img):
        nonlocal best_front_score, best_front_box, best_front_img, best_back_score, best_back_box
        for b in boxes:
            cls_id = int(b.cls[0])
            score = calculate_alignment_score(b)
            if cls_id == 1:  # front-cccd (mặt trước)
                if score > best_front_score:
                    best_front_score = score
                    best_front_img = current_img
                    best_front_box = b
            elif cls_id == 0:  # back-cccd (mặt sau)
                if score > best_back_score:
                    best_back_score = score
                    best_back_box = b

    # Bước 1: Thử góc 0° (ảnh thẳng)
    res_0 = model(img, conf=0.15, verbose=False)
    if len(res_0) > 0 and len(res_0[0].boxes) > 0:
        evaluate_boxes(res_0[0].boxes, img)

    # Bước 2: Thử các góc trực giao (90°, 180°, 270°)
    if best_front_score < 0.88:
        ortho_candidates = [
            (90, cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)),
            (180, cv2.rotate(img, cv2.ROTATE_180)),
            (270, cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE))
        ]
        for angle, rot_img in ortho_candidates:
            try:
                results = model(rot_img, conf=0.15, verbose=False)
                if len(results) > 0 and len(results[0].boxes) > 0:
                    evaluate_boxes(results[0].boxes, rot_img)
            except Exception:
                continue

    # Bước 3: Nếu ảnh bị nghiêng chéo phức tạp (30°, 45°, 60°, 70°, 75°, 80°...)
    if best_front_score < 0.88 and best_back_score < 0.88:
        # Lưới quét góc mịn 15° phủ kín toàn bộ 360°
        skew_angles = [a for a in range(15, 360, 15) if a not in (90, 180, 270)]
        for angle in skew_angles:
            try:
                rot_img = rotate_bound(img, angle)
                results = model(rot_img, conf=0.15, verbose=False)
                if len(results) > 0 and len(results[0].boxes) > 0:
                    evaluate_boxes(results[0].boxes, rot_img)
            except Exception:
                continue

    # 1. Kiểm tra nếu là mặt sau của CCCD
    if best_back_score >= 0.35 and (best_front_box is None or best_back_score > best_front_score + 0.10):
        raise ValueError("Đây là mặt sau của CCCD. Chúng tôi chỉ trích xuất kết quả của mặt trước!")

    # 2. Kiểm tra nếu không tìm thấy thẻ mặt trước hợp lệ
    if best_front_box is None or best_front_score < 0.20:
        if best_back_score >= 0.20:
            raise ValueError("Đây là mặt sau của CCCD. Chúng tôi chỉ trích xuất kết quả của mặt trước!")
        raise ValueError("Sai định dạng CCCD! Hệ thống chỉ hỗ trợ thẻ Căn cước công dân gắn chip chuẩn mới nhất.")

    best_crop_box = best_front_box
    best_oriented_img = best_front_img

    xyxy = best_crop_box.xyxy[0].cpu().numpy() if hasattr(best_crop_box.xyxy[0], 'cpu') else best_crop_box.xyxy[0].numpy()
    x1, y1, x2, y2 = map(int, xyxy)

    h, w = best_oriented_img.shape[:2]
    pad_w = int((x2 - x1) * 0.05)
    pad_h = int((y2 - y1) * 0.05)

    x1_pad, y1_pad = max(0, x1 - pad_w), max(0, y1 - pad_h)
    x2_pad, y2_pad = min(w - 1, x2 + pad_w), min(h - 1, y2 + pad_h)

    crop = best_oriented_img[y1_pad:y2_pad, x1_pad:x2_pad]
    aligned_card = align_and_warp_card(crop)
    return aligned_card