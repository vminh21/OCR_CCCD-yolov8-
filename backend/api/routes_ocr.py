# backend/api/routes_ocr.py
import base64
import logging
import shutil
import cv2
import numpy as np
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Header, HTTPException
from fastapi.responses import JSONResponse

from backend.core.pipeline import process_cccd
from backend.database.connection import SessionLocal
from backend.database.crud import create_scan_and_save_result
from backend.database.models import User
from backend.database.security import decode_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["OCR & AI Pipeline"])


@router.post("/camera-probe", summary="Thăm dò camera thời gian thực để hỗ trợ tự động chụp eKYC")
async def camera_probe_api(file: UploadFile = File(...)):
    contents = await file.read()
    if not contents:
        return {"detected": False, "score": 0.0, "message": "Khung hình rỗng", "color": "white", "box": None}

    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return {"detected": False, "score": 0.0, "message": "Lỗi đọc ảnh", "color": "white", "box": None}

    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. Kiểm tra độ sáng trung bình
    mean_brightness = float(np.mean(gray))
    if mean_brightness < 32:
        return {"detected": False, "side": "none", "score": 0.0, "message": "⚠️ Quá tối! Vui lòng tăng sáng", "color": "yellow", "box": None}
    if mean_brightness > 240:
        return {"detected": False, "side": "none", "score": 0.0, "message": "⚠️ Quá lóa sáng! Tránh nguồn sáng chói", "color": "yellow", "box": None}

    # 2. Kiểm tra độ sắc nét
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if lap_var < 24.0:
        return {"detected": False, "side": "none", "score": 0.0, "message": "⚠️ Ảnh bị rung/mờ! Vui lòng giữ yên", "color": "yellow", "box": None}

    # 3. Sử dụng mô hình YOLO Stage 1 + Stage 2 và VietOCR theo đúng trọng số pipeline
    try:
        from backend.detectors.card_detector import _load_model
        from backend.detectors.field_detector import field_model, extract_fields_yolo
        from backend.ocr.ocr_engine import read_field
        from backend.core.validator import clean_id_number

        card_model = _load_model()
        results = card_model.predict(img, conf=0.18, verbose=False, imgsz=640)

        best_box = None
        best_conf = 0.0
        best_cls = -1

        for r in results:
            for b in r.boxes:
                c = float(b.conf[0])
                if c > best_conf:
                    best_conf = c
                    best_box = b
                    best_cls = int(b.cls[0])

        if best_box is not None and best_conf >= 0.18:
            xyxy = best_box.xyxy[0].cpu().numpy().astype(int)
            x1, y1, x2, y2 = max(0, xyxy[0]), max(0, xyxy[1]), min(w, xyxy[2]), min(h, xyxy[3])
            norm_box = [round(float(x1) / w, 3), round(float(y1) / h, 3), round(float(x2) / w, 3), round(float(y2) / h, 3)]
            bw = x2 - x1
            bh = y2 - y1
            area_ratio = (bw * bh) / (w * h)

            # Trường hợp 1: Phát hiện MẶT SAU CCCD (Class 0: back-cccd)
            if best_cls == 0:
                return {
                    "detected": False,
                    "side": "back",
                    "box": norm_box,
                    "score": round(best_conf, 2),
                    "message": "⚠️ Đây là MẶT SAU CCCD! Vui lòng lật lại mặt trước",
                    "color": "yellow"
                }

            # Kiểm tra cự ly thẻ
            if area_ratio < 0.08:
                return {
                    "detected": False,
                    "side": "front_far",
                    "box": norm_box,
                    "score": round(best_conf, 2),
                    "message": "📏 Đưa thẻ CCCD lại gần camera hơn",
                    "color": "yellow"
                }

            # Trường hợp 2: Kiểm tra tỷ lệ khung thẻ (Aspect Ratio của CCCD ~ 1.58)
            ar = bw / max(1.0, bh)
            if ar < 1.15 or ar > 2.3:
                return {
                    "detected": False,
                    "side": "invalid_card",
                    "box": norm_box,
                    "score": round(best_conf, 2),
                    "message": "❌ Không phải thẻ CCCD! (Sai tỷ lệ khung thẻ)",
                    "color": "red"
                }

            # Bóc tách và kiểm tra thẻ
            card_crop = img[y1:y2, x1:x2]
            if card_crop.size > 0:
                try:
                    f_boxes, _ = extract_fields_yolo(card_crop, field_model)
                    num_fields = len(f_boxes)

                    if num_fields >= 2:
                        id_res = read_field(card_crop, f_boxes, 'id')
                        raw_id = id_res.get('text', '') if isinstance(id_res, dict) else str(id_res)
                        clean_id = clean_id_number(raw_id)

                        if len(clean_id) == 12:
                            return {
                                "detected": True,
                                "side": "front",
                                "box": norm_box,
                                "score": round(best_conf, 2),
                                "message": "✅ CCCD gắn chip hợp lệ! Giữ yên để chụp...",
                                "color": "green",
                                "auto_capture": True
                            }

                        return {
                            "detected": True,
                            "side": "front",
                            "box": norm_box,
                            "score": round(best_conf, 2),
                            "message": "✅ Đã tìm thấy mặt trước CCCD! Giữ yên...",
                            "color": "green",
                            "auto_capture": (best_conf >= 0.70)
                        }
                    else:
                        return {
                            "detected": False,
                            "side": "invalid_card",
                            "box": norm_box,
                            "score": round(best_conf, 2),
                            "message": "❌ Không phải thẻ CCCD! (Không tìm thấy các trường thông tin)",
                            "color": "red"
                        }
                except Exception:
                    return {
                        "detected": True,
                        "side": "front",
                        "box": norm_box,
                        "score": round(best_conf, 2),
                        "message": "✅ Đã thấy thẻ CCCD! Giữ yên...",
                        "color": "green",
                        "auto_capture": (best_conf >= 0.70)
                    }

        # Kiểm tra hình dạng giả mạo không phải CCCD
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 40, 140)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        has_card_shape = False
        best_contour = None
        best_area = 0.0

        for c in contours:
            area = cv2.contourArea(c)
            if area > (w * h * 0.08):
                ratio = area / (w * h)
                if 0.08 <= ratio <= 0.95 and area > best_area:
                    rect = cv2.minAreaRect(c)
                    rw, rh = rect[1]
                    if rw > 0 and rh > 0:
                        ar = max(rw, rh) / min(rw, rh)
                        if 1.15 <= ar <= 2.4:
                            has_card_shape = True
                            best_area = area
                            best_contour = c

        if has_card_shape and best_contour is not None:
            cx, cy, cw_c, ch_c = cv2.boundingRect(best_contour)
            box_candidate = [round(float(cx) / w, 3), round(float(cy) / h, 3), round(float(cx + cw_c) / w, 3), round(float(cy + ch_c) / h, 3)]
            return {
                "detected": False,
                "side": "invalid_card",
                "box": box_candidate,
                "score": 0.0,
                "message": "❌ Không phải thẻ CCCD! (Phát hiện thẻ sinh viên / thẻ khác)",
                "color": "red"
            }

    except Exception as e:
        logger.error(f"Lỗi camera_probe_api: {e}", exc_info=True)

    return {
        "detected": False,
        "side": "none",
        "box": None,
        "score": 0.0,
        "message": "🔍 Đặt mặt trước thẻ CCCD vào khung",
        "color": "white"
    }


@router.post("/image", summary="Trích xuất thông tin CCCD từ file ảnh hoặc video")
async def predict_api(
    file: UploadFile = File(...),
    input_source: Optional[str] = Form("IMAGE"),
    authorization: Optional[str] = Header(None)
):
    ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if ext not in ("jpg", "jpeg", "png", "bmp", "webp", "mp4", "avi", "mov", "mkv", "webm"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file ảnh (JPG, PNG, WEBP) hoặc video (MP4, AVI, MOV, WEBM)!")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="File ảnh rỗng!")

    try:
        temp_dir = Path("data/input")
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / f"upload_{file.filename}"

        with open(temp_path, "wb") as f:
            f.write(contents)

        try:
            result = process_cccd(temp_path)
        except ValueError as ve:
            logger.warning(f"Validation error in process_cccd: {ve}")
            return JSONResponse(
                status_code=400,
                content={"error": str(ve)}
            )
        except Exception as ex:
            logger.error(f"Error in process_cccd: {ex}", exc_info=True)
            return JSONResponse(
                status_code=422,
                content={"error": f"Lỗi xử lý: {str(ex)}"}
            )

        finally:
            if temp_path.exists():
                temp_path.unlink()

        if not result:
            return JSONResponse(
                status_code=422,
                content={"error": "Sai định dạng CCCD! Hệ thống chỉ hỗ trợ thẻ Căn cước công dân gắn chip chuẩn mới nhất."}
            )

        # 1. Nạp ảnh vẽ 8 khung bounding box màu sắc và chuyển sang dạng Base64
        viz_path = Path("data/output/cccd_fields_visualization.jpg")
        if viz_path.exists():
            with open(viz_path, "rb") as f:
                encoded_img = base64.b64encode(f.read()).decode('utf-8')
                result["visualization_base64"] = f"data:image/jpeg;base64,{encoded_img}"

        # 2. Tự động lưu vào PostgreSQL (lưu vào scan_history & cccd_results đủ 8 trường)
        try:
            db_session = SessionLocal()
            try:
                user = None
                if authorization and authorization.startswith("Bearer "):
                    token_str = authorization.split(" ")[1]
                    try:
                        payload = decode_token(token_str)
                        uid = int(payload.get("sub"))
                        user = db_session.query(User).filter(User.id == uid).first()
                    except Exception:
                        pass

                if not user:
                    user = db_session.query(User).first()

                if user:
                    extracted = {
                        "id": result.get("so_cccd"),
                        "name": result.get("ho_ten"),
                        "dob": result.get("ngay_sinh"),
                        "gender": result.get("gioi_tinh"),
                        "nationality": result.get("quoc_tich", "Việt Nam"),
                        "origin_place": result.get("que_quan"),
                        "current_place": result.get("noi_ctru"),
                        "expire_date": result.get("ngay_het_han")
                    }
                    file_stem = Path(file.filename).stem
                    upload_stem = f"upload_{file_stem}"

                    # Lưu ảnh detect phân vùng màu sắc theo scan riêng biệt
                    viz_save_path = Path("data/output/cards") / f"{upload_stem}_viz.jpg"
                    if viz_path.exists():
                        try:
                            shutil.copy(viz_path, viz_save_path)
                            crop_path_val = f"/media/cards/{upload_stem}_viz.jpg"
                        except Exception:
                            crop_path_val = "/media/cccd_fields_visualization.jpg"
                    elif (Path("data/output/cards") / f"{upload_stem}_enhanced.jpg").exists():
                        crop_path_val = f"/media/cards/{upload_stem}_enhanced.jpg"
                    else:
                        crop_path_val = "/media/cccd_fields_visualization.jpg"

                    avatar_file = Path("data/output/avatars") / f"{upload_stem}_avatar.jpg"
                    avatar_path_val = f"/media/avatars/{upload_stem}_avatar.jpg" if avatar_file.exists() else None

                    real_confidence = float(result.get("_confidence", 0.95))
                    real_proc_time = float(result.get("_processing_time", 0.25))

                    source_clean = (input_source or "IMAGE").upper().strip()
                    if source_clean not in ("IMAGE", "WEBCAM", "VIDEO"):
                        if ext in ("mp4", "avi", "mov", "mkv", "webm"):
                            source_clean = "VIDEO"
                        else:
                            source_clean = "IMAGE"

                    scan_obj, res_obj = create_scan_and_save_result(
                        db=db_session,
                        user_id=user.id,
                        extracted_fields=extracted,
                        input_source=source_clean,
                        raw_image_path=crop_path_val,
                        crop_image_path=crop_path_val,
                        avatar_path=avatar_path_val,
                        confidence_score=real_confidence,
                        processing_time=real_proc_time
                    )
                    result["scan_id"] = scan_obj.id
                    result["result_id"] = res_obj.id
                    result["crop_image_path"] = crop_path_val
                    result["avatar_path"] = avatar_path_val
                    result["confidence_score"] = round(real_confidence * 100, 1)
                    result["processing_time"] = real_proc_time
            finally:
                db_session.close()
        except Exception as db_err:
            logger.warning(f"Lưu kết quả vào CSDL thất bại: {db_err}")

        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Lỗi xử lý server: {str(e)}"}
        )
