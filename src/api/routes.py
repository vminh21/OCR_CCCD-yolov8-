# src/api/routes.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.models import User, ScanHistory, CCCDResult, ScanStatistic, AICorrection
from src.database.schemas import (
    UserRegister, UserLogin, UserChangePassword, 
    UserResponse, TokenResponse, CCCDResultEdit,
    CCCDResultResponse, ScanHistoryResponse, ScanStatisticResponse, AICorrectionResponse
)
from src.database.security import (
    create_access_token, get_current_user
)
from src.database.crud import (
    register_user, authenticate_user, change_user_password,
    get_user_by_username, get_user_by_email,
    get_user_results, get_result_by_id, delete_cccd_result, get_user_statistics,
    edit_cccd_result_and_record_corrections, get_all_user_corrections
)

router = APIRouter(prefix="/api")

# ==============================================================================
# BẢNG 1: USER (QUẢN LÝ TÀI KHOẢN)
# ==============================================================================

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Đăng ký tài khoản")
def api_register(user_in: UserRegister, db: Session = Depends(get_db)):
    if get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Tên tài khoản đã tồn tại!")
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email đã được sử dụng!")

    user = register_user(db, user_in)
    return user

@router.post("/auth/login", response_model=TokenResponse, summary="Đăng nhập tài khoản")
def api_login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Sai tên đăng nhập hoặc mật khẩu!")

    access_token = create_access_token(data={"sub": str(user.id), "username": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/auth/logout", summary="Đăng xuất")
def api_logout(current_user: User = Depends(get_current_user)):
    return {"message": "Đăng xuất thành công"}

@router.post("/auth/change-password", summary="Đổi mật khẩu")
def api_change_password(
    data: UserChangePassword, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    success = change_user_password(db, current_user, data.old_password, data.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Mật khẩu cũ không chính xác!")
    return {"message": "Đổi mật khẩu thành công!"}

@router.get("/auth/me", response_model=UserResponse, summary="Thông tin người dùng hiện tại")
def api_get_me(current_user: User = Depends(get_current_user)):
    return current_user

# ==============================================================================
# BẢNG 2: SCAN_HISTORY (LỊCH SỬ CÁC LẦN QUÉT)
# ==============================================================================

@router.get("/history", response_model=List[ScanHistoryResponse], summary="Xem danh sách lịch sử các lần quét")
def api_get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scans = db.query(ScanHistory).filter(ScanHistory.user_id == current_user.id).order_by(ScanHistory.created_at.desc()).all()
    return scans

# ==============================================================================
# BẢNG 3: CCCD_RESULTS (BẢNG LƯU KẾT QUẢ ĐỦ 8 TRƯỜNG CCCD)
# ==============================================================================

@router.get("/results", summary="Xem danh sách kết quả CCCD đã lưu (Đủ 8 trường)")
def api_get_results(
    search: Optional[str] = Query(None, description="Tìm kiếm theo Số CCCD hoặc Họ tên"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items, total = get_user_results(db, current_user.id, search, limit, offset)
    out = []
    for r in items:
        out.append({
            "id": r.id,
            "history_id": r.history_id,
            "id_number": r.id_number,
            "full_name": r.full_name,
            "dob": r.dob,
            "gender": r.gender,
            "nationality": r.nationality or "Việt Nam",
            "origin_location": r.origin_location,
            "residence": r.residence,
            "expiry_date": r.expiry_date,
            "saved_at": r.saved_at,
            "crop_image_path": r.scan.crop_image_path if r.scan else "/media/cccd_fields_visualization.jpg",
            "avatar_path": r.scan.avatar_path if r.scan else None,
            "status": r.scan.status if r.scan else "COMPLETED"
        })
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": out
    }

@router.get("/results/{result_id}", summary="Xem chi tiết 1 kết quả CCCD")
def api_get_result_detail(
    result_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = get_result_by_id(db, result_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Không tìm thấy kết quả CCCD!")
    return {
        "id": result.id,
        "history_id": result.history_id,
        "id_number": result.id_number,
        "full_name": result.full_name,
        "dob": result.dob,
        "gender": result.gender,
        "nationality": result.nationality or "Việt Nam",
        "origin_location": result.origin_location,
        "residence": result.residence,
        "expiry_date": result.expiry_date,
        "saved_at": result.saved_at,
        "crop_image_path": result.scan.crop_image_path if result.scan else "/media/cccd_fields_visualization.jpg",
        "avatar_path": result.scan.avatar_path if result.scan else None,
        "raw_image_path": result.scan.raw_image_path if result.scan else None,
        "confidence_score": result.scan.confidence_score if result.scan else 0.96,
        "status": result.scan.status if result.scan else "COMPLETED"
    }

@router.put("/results/{result_id}", response_model=CCCDResultResponse, summary="Chỉnh sửa kết quả CCCD đã lưu")
def api_edit_result(
    result_id: int,
    edit_data: CCCDResultEdit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        updated = edit_cccd_result_and_record_corrections(db, result_id, current_user.id, edit_data)
        return updated
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/results/{result_id}", summary="Xóa kết quả CCCD")
def api_delete_result(
    result_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = delete_cccd_result(db, result_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy kết quả CCCD hoặc không có quyền xóa!")
    return {"message": f"Đã xóa thành công hồ sơ CCCD #{result_id}"}

# ==============================================================================
# BẢNG 4: SCAN_STATISTICS (QUẢN LÝ THỐNG KÊ)
# ==============================================================================

@router.get("/statistics", response_model=ScanStatisticResponse, summary="Xem thống kê lượt quét")
def api_get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stat = get_user_statistics(db, current_user.id)
    return stat

# ==============================================================================
# BẢNG 5: AI_CORRECTIONS (ĐÁNH GIÁ ĐỘ ĐÚNG CỦA AI VÀ LỊCH SỬ CHỈNH SỬA)
# ==============================================================================

@router.get("/corrections", response_model=List[AICorrectionResponse], summary="Xem toàn bộ đánh giá độ đúng AI & lịch sử chỉnh sửa")
def api_get_corrections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_all_user_corrections(db, current_user.id)
