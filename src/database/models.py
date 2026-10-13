# src/database/models.py
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Float, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from src.database.connection import Base

# 1. BẢNG TÀI KHOẢN NGƯỜI DÙNG
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Quan hệ
    scans = relationship("ScanHistory", back_populates="user", cascade="all, delete-orphan")
    results = relationship("CCCDResult", back_populates="user", cascade="all, delete-orphan")
    statistics = relationship("ScanStatistic", back_populates="user", uselist=False, cascade="all, delete-orphan")
    corrections = relationship("AICorrection", back_populates="user", cascade="all, delete-orphan")


# 2. BẢNG LỊCH SỬ CÁC LẦN QUÉT
class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    raw_image_path = Column(Text, nullable=True)
    crop_image_path = Column(Text, nullable=True)
    avatar_path = Column(Text, nullable=True)
    input_source = Column(String(20), default="IMAGE")   # IMAGE, WEBCAM, VIDEO
    status = Column(String(50), default="COMPLETED")     # COMPLETED, EDITED
    confidence_score = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Quan hệ
    user = relationship("User", back_populates="scans")
    result = relationship("CCCDResult", back_populates="scan", uselist=False, cascade="all, delete-orphan")
    corrections = relationship("AICorrection", back_populates="scan", cascade="all, delete-orphan")


# 3. BẢNG LƯU KẾT QUẢ ĐỦ 8 TRƯỜNG CCCD
class CCCDResult(Base):
    __tablename__ = "cccd_results"

    id = Column(Integer, primary_key=True, index=True)
    history_id = Column(Integer, ForeignKey("scan_history.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # ĐỦ 8 TRƯỜNG MẶT TRƯỚC CCCD:
    id_number = Column(String(12), index=True, nullable=False)               # 1. Số CCCD
    full_name = Column(String(100), index=True, nullable=False)              # 2. Họ và tên
    dob = Column(Date, nullable=True)                                        # 3. Ngày sinh
    gender = Column(String(10), nullable=True)                               # 4. Giới tính
    nationality = Column(String(50), default="Việt Nam", nullable=True)      # 5. Quốc tịch (Bổ sung đầy đủ)
    origin_location = Column(Text, nullable=True)                            # 6. Quê quán
    residence = Column(Text, nullable=True)                                  # 7. Nơi thường trú
    expiry_date = Column(Date, nullable=True)                                # 8. Có giá trị đến

    saved_at = Column(DateTime, server_default=func.now())

    # Quan hệ
    scan = relationship("ScanHistory", back_populates="result")
    user = relationship("User", back_populates="results")


# 4. BẢNG THỐNG KÊ HỆ THỐNG
class ScanStatistic(Base):
    __tablename__ = "scan_statistics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    total_scans = Column(Integer, default=0)
    image_scans = Column(Integer, default=0)
    webcam_scans = Column(Integer, default=0)
    video_scans = Column(Integer, default=0)
    edited_scans = Column(Integer, default=0)
    avg_confidence = Column(Float, default=0.0)
    avg_processing_time = Column(Float, default=0.0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="statistics")


# 5. BẢNG PHÂN CHIA ĐỘ ĐÚNG CỦA AI VÀ NGƯỜI DÙNG SỬA GÌ
class AICorrection(Base):
    __tablename__ = "ai_corrections"

    id = Column(Integer, primary_key=True, index=True)
    history_id = Column(Integer, ForeignKey("scan_history.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    field_name = Column(String(50), nullable=False)       # Tên trường (id_number, full_name, nationality,...)
    ai_prediction = Column(Text, nullable=True)           # Giá trị AI đọc được ban đầu
    user_corrected = Column(Text, nullable=False)         # Giá trị người dùng sửa lại
    is_correct = Column(Boolean, default=False)           # AI đoán đúng (True) hay sai (False)
    ai_confidence = Column(Float, nullable=True)          # Độ tin cậy của AI ở trường này
    corrected_at = Column(DateTime, server_default=func.now())

    scan = relationship("ScanHistory", back_populates="corrections")
    user = relationship("User", back_populates="corrections")
