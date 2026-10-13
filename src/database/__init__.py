# src/database/__init__.py
from src.database.connection import engine, SessionLocal, Base, get_db
from src.database.models import User, ScanHistory, CCCDResult, ScanStatistic, AICorrection
from src.database.security import (
    hash_password, verify_password, 
    create_access_token, get_current_user
)

__all__ = [
    "engine", "SessionLocal", "Base", "get_db",
    "User", "ScanHistory", "CCCDResult", "ScanStatistic", "AICorrection",
    "hash_password", "verify_password",
    "create_access_token", "get_current_user"
]
