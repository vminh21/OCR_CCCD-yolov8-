import base64
import json
import logging
import shutil
import cv2
import numpy as np
from pathlib import Path
from typing import Optional


from fastapi import APIRouter, UploadFile, File, Form, Header, HTTPException
from fastapi.responses import JSONResponse

from backend.core.pipeline import process_cccd
from backend.core.ai_evaluator import (
    evaluate_pipeline_with_ai,
    is_system_key_configured,
    test_api_key,
    resolve_api_key
)
from backend.database.connection import SessionLocal
from backend.database.crud import create_scan_and_save_result
from backend.database.models import User
from backend.database.security import decode_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["OCR & AI Pipeline"])



@router.post("/camera-probe", summary="Thăm dò camera thời gian thực để hỗ trợ tự động chụp eKYC")
def camera_probe_api(file: UploadFile = File(...)):
    contents = file.file.read()
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
    if mean_brightness < 28:
        return {"detected": False, "side": "none", "score": 0.0, "message": "⚠️ Quá tối! Vui lòng tăng sáng", "color": "yellow", "box": None}
    if mean_brightness > 245:
        return {"detected": False, "side": "none", "score": 0.0, "message": "⚠️ Quá lóa sáng! Tránh nguồn sáng chói", "color": "yellow", "box": None}

    # 2. Kiểm tra độ sắc nét (ngưỡng 14.0 cho webcam trực tiếp)
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if lap_var < 14.0:
        return {"detected": False, "side": "none", "score": 0.0, "message": "⚠️ Ảnh bị rung/mờ! Vui lòng giữ yên", "color": "yellow", "box": None}

    # 3. Sử dụng mô hình YOLO Stage 1 + Stage 2 để kiểm tra thẻ thời gian thực
    try:
        from backend.detectors.card_detector import _load_model
        from backend.detectors.field_detector import extract_fields_yolo

        card_model = _load_model()
        # Chạy suy luận nhanh imgsz=416 và conf=0.20 để bắt nhạy thẻ trên webcam
        results = card_model.predict(img, conf=0.20, verbose=False, imgsz=416)

        best_front_box = None
        best_front_conf = 0.0
        best_back_box = None
        best_back_conf = 0.0

        for r in results:
            for b in r.boxes:
                c = float(b.conf[0])
                cls_id = int(b.cls[0])
                if cls_id == 1 and c > best_front_conf:
                    best_front_conf = c
                    best_front_box = b
                elif cls_id == 0 and c > best_back_conf:
                    best_back_conf = c
                    best_back_box = b

        # Trường hợp 1: Phát hiện MẶT SAU CCCD (Class 0: back-cccd)
        if best_back_box is not None and best_back_conf >= 0.35 and (best_front_box is None or best_back_conf >= best_front_conf - 0.05):
            xyxy_back = best_back_box.xyxy[0].cpu().numpy().astype(int)
            x1, y1, x2, y2 = max(0, xyxy_back[0]), max(0, xyxy_back[1]), min(w, xyxy_back[2]), min(h, xyxy_back[3])
            norm_box = [round(float(x1) / w, 3), round(float(y1) / h, 3), round(float(x2) / w, 3), round(float(y2) / h, 3)]
            return {
                "detected": False,
                "is_cccd": True,
                "side": "back",
                "box": norm_box,
                "score": round(best_back_conf, 2),
                "message": "⚠️ Đây là mặt sau của CCCD! Vui lòng lật lại mặt trước",
                "color": "yellow",
                "can_capture": False,
                "auto_capture": False
            }

        # Trường hợp 2: Có box mặt trước từ mô hình Stage 1
        if best_front_box is not None and best_front_conf >= 0.22:
            xyxy = best_front_box.xyxy[0].cpu().numpy().astype(int)
            x1, y1, x2, y2 = max(0, xyxy[0]), max(0, xyxy[1]), min(w, xyxy[2]), min(h, xyxy[3])
            norm_box = [round(float(x1) / w, 3), round(float(y1) / h, 3), round(float(x2) / w, 3), round(float(y2) / h, 3)]
            bw = x2 - x1
            bh = y2 - y1
            area_ratio = (bw * bh) / (w * h)

            # Kiểm tra cự ly thẻ
            if area_ratio < 0.05:
                return {
                    "detected": False,
                    "is_cccd": True,
                    "side": "front_far",
                    "box": norm_box,
                    "score": round(best_front_conf, 2),
                    "message": "📏 Đưa thẻ CCCD lại gần camera hơn",
                    "color": "yellow",
                    "can_capture": False,
                    "auto_capture": False
                }

            # Kiểm tra tỷ lệ khung thẻ (Aspect Ratio của CCCD ~ 1.58)
            ar = bw / max(1.0, bh)
            if ar < 1.05 or ar > 2.5:
                if 0.40 <= ar <= 0.85:
                    return {
                        "detected": False,
                        "is_cccd": True,
                        "side": "front_vertical",
                        "box": norm_box,
                        "score": round(best_front_conf, 2),
                        "message": "📐 Vui lòng xoay ngang thẻ CCCD",
                        "color": "yellow",
                        "can_capture": False,
                        "auto_capture": False
                    }
                return {
                    "detected": False,
                    "is_cccd": False,
                    "side": "invalid_card",
                    "box": norm_box,
                    "score": round(best_front_conf, 2),
                    "message": "❌ Không phải thẻ CCCD! Không thể chụp thẻ khác",
                    "color": "red",
                    "can_capture": False,
                    "auto_capture": False
                }

            # Bóc tách kiểm tra trường thẻ bằng Stage 2 YOLO
            card_crop = img[y1:y2, x1:x2]
            if card_crop.size > 0:
                try:
                    field_crops = extract_fields_yolo(card_crop)
                    num_fields = len(field_crops)

                    # Thẻ hợp lệ: phát hiện >= 2 trường hoặc confidence Stage 1 cao
                    if num_fields >= 2 or best_front_conf >= 0.40:
                        is_auto = (best_front_conf >= 0.70 and num_fields >= 3)
                        return {
                            "detected": True,
                            "is_cccd": True,
                            "side": "front",
                            "box": norm_box,
                            "score": round(best_front_conf, 2),
                            "message": "✅ CCCD gắn chip hợp lệ! Giữ yên để chụp...",
                            "color": "green",
                            "can_capture": True,
                            "auto_capture": is_auto
                        }
                    elif num_fields == 0 and best_front_conf < 0.30:
                        # Không có trường nào và conf thấp -> Thẻ lạ
                        return {
                            "detected": False,
                            "is_cccd": False,
                            "side": "invalid_card",
                            "box": norm_box,
                            "score": round(best_front_conf, 2),
                            "message": "❌ Không phải thẻ CCCD! Không thể chụp thẻ khác",
                            "color": "red",
                            "can_capture": False,
                            "auto_capture": False
                        }
                    else:
                        return {
                            "detected": True,
                            "is_cccd": True,
                            "side": "front",
                            "box": norm_box,
                            "score": round(best_front_conf, 2),
                            "message": "✅ Đã tìm thấy mặt trước CCCD! Giữ yên để chụp...",
                            "color": "green",
                            "can_capture": True,
                            "auto_capture": False
                        }
                except Exception as e:
                    logger.warning(f"Lỗi extract_fields_yolo trong probe: {e}")
                    return {
                        "detected": True,
                        "is_cccd": True,
                        "side": "front",
                        "box": norm_box,
                        "score": round(best_front_conf, 2),
                        "message": "✅ Đã tìm thấy mặt trước CCCD! Giữ yên để chụp...",
                        "color": "green",
                        "can_capture": True,
                        "auto_capture": False
                    }

        # Trường hợp 3: Kiểm tra hình dạng thẻ khác qua Edge / Contour nếu YOLO không nhận
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 40, 140)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        has_card_shape = False
        best_contour = None
        best_area = 0.0

        for c in contours:
            area = cv2.contourArea(c)
            if area > (w * h * 0.10):
                ratio = area / (w * h)
                if 0.10 <= ratio <= 0.90 and area > best_area:
                    rect = cv2.minAreaRect(c)
                    rw, rh = rect[1]
                    if rw > 0 and rh > 0:
                        ar = max(rw, rh) / min(rw, rh)
                        if 1.25 <= ar <= 2.2:
                            has_card_shape = True
                            best_area = area
                            best_contour = c

        if has_card_shape and best_contour is not None and best_front_conf < 0.20 and best_back_conf < 0.20:
            cx, cy, cw_c, ch_c = cv2.boundingRect(best_contour)
            box_candidate = [round(float(cx) / w, 3), round(float(cy) / h, 3), round(float(cx + cw_c) / w, 3), round(float(cy + ch_c) / h, 3)]
            candidate_crop = img[cy:cy+ch_c, cx:cx+cw_c]
            num_cand_fields = 0
            if candidate_crop.size > 0:
                try:
                    c_fields = extract_fields_yolo(candidate_crop)
                    num_cand_fields = len(c_fields)
                except Exception:
                    pass

            if num_cand_fields >= 2:
                return {
                    "detected": True,
                    "is_cccd": True,
                    "side": "front",
                    "box": box_candidate,
                    "score": 0.50,
                    "message": "✅ CCCD gắn chip hợp lệ! Giữ yên để chụp...",
                    "color": "green",
                    "can_capture": True,
                    "auto_capture": False
                }
            else:
                return {
                    "detected": False,
                    "is_cccd": False,
                    "side": "invalid_card",
                    "box": box_candidate,
                    "score": 0.0,
                    "message": "❌ Không phải thẻ CCCD! Không thể chụp thẻ khác",
                    "color": "red",
                    "can_capture": False,
                    "auto_capture": False
                }

    except Exception as e:
        logger.error(f"Lỗi camera_probe_api: {e}", exc_info=True)

    return {
        "detected": False,
        "is_cccd": False,
        "side": "none",
        "box": None,
        "score": 0.0,
        "message": "🔍 Căn mặt trước thẻ CCCD vào khung",
        "color": "white",
        "can_capture": False,
        "auto_capture": False
    }


@router.post("/image", summary="Trích xuất thông tin CCCD từ file ảnh hoặc video")
async def predict_api(
    file: UploadFile = File(...),
    input_source: Optional[str] = Form("IMAGE"),
    evaluate_with_ai: Optional[bool] = Form(False),
    authorization: Optional[str] = Header(None),
    x_ai_api_key: Optional[str] = Header(None),
    x_ai_provider: Optional[str] = Header("gemini")
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
        file_stem = Path(file.filename).stem
        upload_stem = f"upload_{file_stem}"
        crop_path_val = "/media/cccd_fields_visualization.jpg"

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

        # 3. Thẩm định độ chính xác bằng External Vision AI nếu được yêu cầu
        if evaluate_with_ai:
            try:
                eval_bytes = contents
                crop_local_path = Path("data/output/cards") / f"{upload_stem}_enhanced.jpg"
                if not crop_local_path.exists():
                    crop_local_path = Path("data/output/cards") / f"{upload_stem}_viz.jpg"
                if crop_local_path.exists():
                    with open(crop_local_path, "rb") as cf:
                        eval_bytes = cf.read()

                eval_res = evaluate_pipeline_with_ai(
                    image_bytes=eval_bytes,
                    local_result=result,
                    user_key=x_ai_api_key,
                    provider=x_ai_provider or "gemini"
                )
                result["ai_evaluation"] = eval_res
            except Exception as eval_err:
                logger.warning(f"Thẩm định AI thất bại: {eval_err}")
                result["ai_evaluation"] = {
                    "status": "error",
                    "message": str(eval_err),
                    "overall_accuracy": None
                }
        else:
            result["ai_evaluation"] = None

        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Lỗi xử lý server: {str(e)}"}
        )


@router.get("/evaluate-status", summary="Kiểm tra trạng thái cấu hình AI Key của hệ thống")
def get_evaluate_status():
    has_gemini = is_system_key_configured("gemini")
    has_openai = is_system_key_configured("openai")
    gemini_key, _ = resolve_api_key(user_key=None, provider="gemini")
    openai_key, _ = resolve_api_key(user_key=None, provider="openai")

    masked_gemini = f"{gemini_key[:8]}...{gemini_key[-4:]}" if gemini_key and len(gemini_key) > 12 else None
    masked_openai = f"{openai_key[:6]}...{openai_key[-4:]}" if openai_key and len(openai_key) > 10 else None

    return {
        "system_gemini_configured": has_gemini,
        "system_openai_configured": has_openai,
        "system_key_configured": has_gemini or has_openai,
        "default_provider": "gemini" if has_gemini else ("openai" if has_openai else "gemini"),
        "system_gemini_masked": masked_gemini,
        "system_openai_masked": masked_openai
    }


@router.post("/evaluate-test-key", summary="Kiểm tra kết nối và tính hợp lệ của API Key")
def post_test_api_key(
    api_key: Optional[str] = Form(None),
    provider: Optional[str] = Form("gemini")
):
    provider_clean = (provider or "gemini").lower().strip()
    resolved_key, source = resolve_api_key(user_key=api_key, provider=provider_clean)
    if not resolved_key:
        return {
            "valid": False,
            "provider": provider_clean,
            "source": "none",
            "message": f"Chưa cấu hình API Key cho {provider_clean}. Vui lòng nhập key hoặc thêm vào file .env."
        }

    test_res = test_api_key(api_key=resolved_key, provider=provider_clean)
    test_res["source"] = source
    test_res["masked_key"] = f"{resolved_key[:8]}...{resolved_key[-4:]}" if len(resolved_key) > 12 else resolved_key
    return test_res


@router.post("/evaluate-on-demand", summary="Thẩm định độ chính xác theo yêu cầu cho kết quả đã quét")
async def evaluate_on_demand_api(
    file: UploadFile = File(...),
    local_data_json: str = Form(...),
    x_ai_api_key: Optional[str] = Header(None),
    x_ai_provider: Optional[str] = Header("gemini")
):
    try:
        contents = await file.read()
        local_data = json.loads(local_data_json)
        eval_res = evaluate_pipeline_with_ai(
            image_bytes=contents,
            local_result=local_data,
            user_key=x_ai_api_key,
            provider=x_ai_provider or "gemini"
        )
        return eval_res
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": f"Lỗi thẩm định: {str(e)}"}
        )

