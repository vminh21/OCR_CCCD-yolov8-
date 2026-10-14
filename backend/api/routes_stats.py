# backend/api/routes_stats.py
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.api.deps import get_db, get_current_user
from backend.database.models import User
from backend.database.schemas import ScanStatisticResponse, AICorrectionResponse
from backend.database.crud import get_user_statistics, get_all_user_corrections

router = APIRouter(tags=["Statistics & AI Quality"])


@router.get("/statistics", response_model=ScanStatisticResponse, summary="Xem thống kê lượt quét")
def api_get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stat = get_user_statistics(db, current_user.id)
    return stat


@router.get("/corrections", response_model=List[AICorrectionResponse], summary="Xem toàn bộ đánh giá độ đúng AI & lịch sử chỉnh sửa")
def api_get_corrections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_all_user_corrections(db, current_user.id)
