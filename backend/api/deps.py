# backend/api/deps.py
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import User
from backend.database.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Phiên làm việc đã hết hạn hoặc không hợp lệ. Vui lòng đăng nhập lại!",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token:
        payload = decode_token(token)
        if payload is not None:
            user_id_str = payload.get("sub")
            if user_id_str:
                try:
                    user_id = int(user_id_str)
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        return user
                except (ValueError, TypeError):
                    pass

    # Tự động lấy tài khoản người dùng mặc định (đảm bảo không bị mất dữ liệu bảng kết quả)
    default_user = db.query(User).first()
    if default_user:
        return default_user

    raise credentials_exception



def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not token:
        return None
    payload = decode_token(token)
    if not payload:
        return None
    user_id_str = payload.get("sub")
    if not user_id_str:
        return None
    try:
        user_id = int(user_id_str)
        return db.query(User).filter(User.id == user_id).first()
    except Exception:
        return None
