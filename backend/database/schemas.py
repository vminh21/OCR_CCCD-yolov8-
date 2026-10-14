from typing import Optional, List, Union
from datetime import date, datetime
from pydantic import BaseModel, Field

# ==============================================================================
# 1. USER SCHEMAS (BẢNG 1: USERS)
# ==============================================================================

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=100)
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=100)

class UserLogin(BaseModel):
    username: str
    password: str

class UserChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ==============================================================================
# 2. SCAN HISTORY SCHEMAS (BẢNG 2: SCAN_HISTORY)
# ==============================================================================

class ScanHistoryResponse(BaseModel):
    id: int
    user_id: int
    raw_image_path: Optional[str] = None
    crop_image_path: Optional[str] = None
    avatar_path: Optional[str] = None
    input_source: Optional[str] = "IMAGE"
    status: Optional[str] = "COMPLETED"
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ==============================================================================
# 3. CCCD RESULTS SCHEMAS (BẢNG 3: CCCD_RESULTS - ĐỦ 8 TRƯỜNG DỮ LIỆU)
# ==============================================================================

class CCCDResultEdit(BaseModel):
    id_number: Optional[str] = None
    full_name: Optional[str] = None
    dob: Optional[Union[date, str]] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None           # Trường 5: Quốc tịch
    origin_location: Optional[str] = None
    residence: Optional[str] = None
    expiry_date: Optional[Union[date, str]] = None

class CCCDResultResponse(BaseModel):
    id: int
    history_id: int
    user_id: int
    id_number: str
    full_name: str
    dob: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = "Việt Nam"     # Đủ 8 trường
    origin_location: Optional[str] = None
    residence: Optional[str] = None
    expiry_date: Optional[date] = None
    saved_at: datetime

    class Config:
        from_attributes = True

# ==============================================================================
# 4. STATISTICS SCHEMAS (BẢNG 4: SCAN_STATISTICS)
# ==============================================================================

class ScanStatisticResponse(BaseModel):
    total_scans: int
    image_scans: int
    webcam_scans: int
    video_scans: int
    edited_scans: int
    avg_confidence: float
    avg_processing_time: float
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==============================================================================
# 5. AI CORRECTIONS SCHEMAS (BẢNG 5: AI_CORRECTIONS - ĐỘ ĐÚNG AI & ĐỐI SOÁT)
# ==============================================================================

class AICorrectionResponse(BaseModel):
    id: int
    history_id: int
    user_id: int
    field_name: str
    ai_prediction: Optional[str] = None
    user_corrected: str
    is_correct: bool
    ai_confidence: Optional[float] = None
    corrected_at: datetime

    class Config:
        from_attributes = True
