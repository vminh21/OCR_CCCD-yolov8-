# backend/api/routes_auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.deps import get_db, get_current_user
from backend.database.models import User
from backend.database.schemas import (
    UserRegister, UserLogin, UserChangePassword, 
    UserResponse, TokenResponse
)
from backend.database.security import create_access_token
from backend.database.crud import (
    register_user, authenticate_user, change_user_password,
    get_user_by_username, get_user_by_email
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Đăng ký tài khoản")
def api_register(user_in: UserRegister, db: Session = Depends(get_db)):
    if get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Tên tài khoản đã tồn tại!")
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email đã được sử dụng!")

    user = register_user(db, user_in)
    return user


@router.post("/login", response_model=TokenResponse, summary="Đăng nhập tài khoản")
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


@router.post("/logout", summary="Đăng xuất")
def api_logout(current_user: User = Depends(get_current_user)):
    return {"message": "Đăng xuất thành công"}


@router.post("/change-password", summary="Đổi mật khẩu")
def api_change_password(
    data: UserChangePassword, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    success = change_user_password(db, current_user, data.old_password, data.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Mật khẩu cũ không chính xác!")
    return {"message": "Đổi mật khẩu thành công!"}


@router.get("/me", response_model=UserResponse, summary="Thông tin người dùng hiện tại")
def api_get_me(current_user: User = Depends(get_current_user)):
    return current_user
