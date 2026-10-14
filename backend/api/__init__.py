# backend/api/__init__.py
from fastapi import APIRouter
from backend.api.routes_auth import router as auth_router
from backend.api.routes_results import router as results_router
from backend.api.routes_stats import router as stats_router
from backend.api.routes_ocr import router as ocr_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(results_router)
api_router.include_router(stats_router)

__all__ = ["api_router", "ocr_router"]
