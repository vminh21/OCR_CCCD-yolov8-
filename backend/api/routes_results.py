# backend/api/routes_results.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.api.deps import get_db, get_current_user
from backend.database.models import User, ScanHistory
from backend.database.schemas import (
    CCCDResultEdit, CCCDResultResponse, ScanHistoryResponse
)
from backend.database.crud import (
    get_user_results, get_result_by_id, delete_cccd_result,
    edit_cccd_result_and_record_corrections
)

router = APIRouter(tags=["CCCD Results & History"])


@router.get("/history", response_model=List[ScanHistoryResponse], summary="Xem danh sách lịch sử các lần quét")
def api_get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scans = db.query(ScanHistory).filter(ScanHistory.user_id == current_user.id).order_by(ScanHistory.created_at.desc()).all()
    return scans


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
