# backend/api/routes_stats.py
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.api.deps import get_db, get_current_user
from backend.database.models import User
from backend.database.schemas import (
    ScanStatisticResponse,
    AICorrectionResponse,
    DemographicsResponse,
    AIQualityResponse
)
from backend.database.crud import (
    get_user_statistics,
    get_all_user_corrections,
    get_user_demographics,
    get_user_ai_quality
)

router = APIRouter(tags=["Statistics & AI Quality"])


@router.get("/statistics", response_model=ScanStatisticResponse, summary="Xem thống kê lượt quét tổng quan")
def api_get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_statistics(db, current_user.id)


@router.get("/statistics/demographics", response_model=DemographicsResponse, summary="Xem thống kê nhân khẩu học (Nam/Nữ, Tỉnh thành, Độ tuổi)")
def api_get_demographics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_demographics(db, current_user.id)


@router.get("/statistics/ai-quality", response_model=AIQualityResponse, summary="Xem đánh giá chi tiết độ đúng và tỷ lệ lỗi từng trường của AI")
def api_get_ai_quality(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_ai_quality(db, current_user.id)


@router.get("/corrections", response_model=List[AICorrectionResponse], summary="Xem toàn bộ đánh giá độ đúng AI & lịch sử chỉnh sửa")
def api_get_corrections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_all_user_corrections(db, current_user.id)

