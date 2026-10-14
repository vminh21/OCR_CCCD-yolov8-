# src/database/__init__.py
from backend.database.connection import engine, SessionLocal, Base, get_db
from backend.database.models import User, ScanHistory, CCCDResult, ScanStatistic, AICorrection
from backend.database.security import (
    hash_password, verify_password, 
    create_access_token, get_current_user
)

__all__ = [
    "engine", "SessionLocal", "Base", "get_db",
    "User", "ScanHistory", "CCCDResult", "ScanStatistic", "AICorrection",
    "hash_password", "verify_password",
    "create_access_token", "get_current_user"
]
