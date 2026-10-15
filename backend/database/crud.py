# src/database/crud.py
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc

from backend.database.models import User, ScanHistory, CCCDResult, ScanStatistic, AICorrection
from backend.database.schemas import UserRegister, CCCDResultEdit
from backend.database.security import hash_password, verify_password

# ==============================================================================
# BẢNG 1: USER (QUẢN LÝ TÀI KHOẢN)
# ==============================================================================

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def register_user(db: Session, user_in: UserRegister) -> User:
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        full_name=user_in.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Khởi tạo bản ghi thống kê ban đầu cho người dùng
    stat = ScanStatistic(user_id=new_user.id)
    db.add(stat)
    db.commit()

    return new_user

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user:
        # Tự động khởi tạo tài khoản mẫu nếu đăng nhập lần đầu
        if username == "minh_final" and password == "password123":
            user = User(
                username="minh_final",
                email="minh_final@example.com",
                full_name="Nguyễn Văn Minh (Demo)",
                password_hash=hash_password("password123")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            stat = ScanStatistic(user_id=user.id)
            db.add(stat)
            db.commit()
            return user
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def change_user_password(db: Session, user: User, old_password: str, new_password: str) -> bool:
    if not verify_password(old_password, user.password_hash):
        return False
    user.password_hash = hash_password(new_password)
    db.commit()
    return True

# ==============================================================================
# BẢNG 2 & BẢNG 3: QUÉT THẺ & LƯU KẾT QUẢ ĐỦ 8 TRƯỜNG CCCD
# ==============================================================================

def parse_date_safe(date_str: Optional[str]) -> Optional[date]:
    if not date_str:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except Exception:
            pass
    return None

def create_scan_and_save_result(
    db: Session,
    user_id: int,
    extracted_fields: Dict[str, Any],
    input_source: str = "IMAGE",
    raw_image_path: str = None,
    crop_image_path: str = None,
    avatar_path: str = None,
    confidence_score: float = 0.95,
    processing_time: float = 0.15
) -> Tuple[ScanHistory, CCCDResult]:
    """Tạo lượt quét trong scan_history và lưu hồ sơ kết quả chính thức vào cccd_results (8 trường)"""
    # 1. Lưu vào Bảng 2: scan_history
    scan = ScanHistory(
        user_id=user_id,
        raw_image_path=raw_image_path,
        crop_image_path=crop_image_path,
        avatar_path=avatar_path,
        input_source=input_source,
        status="COMPLETED",
        confidence_score=confidence_score,
        processing_time=processing_time
    )
    db.add(scan)
    db.flush() # Lấy scan.id

    # 2. Lưu vào Bảng 3: cccd_results (Đủ 8 trường)
    dob = parse_date_safe(extracted_fields.get("dob") or extracted_fields.get("ngay_sinh"))
    exp = parse_date_safe(extracted_fields.get("expire_date") or extracted_fields.get("ngay_het_han"))

    result = CCCDResult(
        history_id=scan.id,
        user_id=user_id,
        id_number=extracted_fields.get("id") or extracted_fields.get("so_cccd") or "000000000000",
        full_name=extracted_fields.get("name") or extracted_fields.get("ho_ten") or "CHƯA RÕ",
        dob=dob,
        gender=extracted_fields.get("gender") or extracted_fields.get("gioi_tinh"),
        nationality=extracted_fields.get("nationality") or extracted_fields.get("quoc_tich") or "Việt Nam", # Trường 5
        origin_location=extracted_fields.get("origin_place") or extracted_fields.get("que_quan"),
        residence=extracted_fields.get("current_place") or extracted_fields.get("thuong_tru"),
        expiry_date=exp
    )
    db.add(result)
    db.commit()
    db.refresh(scan)
    db.refresh(result)

    # 3. Tự động cập nhật Bảng 4: scan_statistics
    update_statistics_on_scan(db, user_id, input_source, confidence_score, processing_time)

    return scan, result

def get_user_results(
    db: Session,
    user_id: int,
    search: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> Tuple[List[CCCDResult], int]:
    query = db.query(CCCDResult).filter(CCCDResult.user_id == user_id)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                CCCDResult.id_number.ilike(search_fmt),
                CCCDResult.full_name.ilike(search_fmt)
            )
        )
    total = query.count()
    items = query.order_by(desc(CCCDResult.saved_at)).offset(offset).limit(limit).all()
    return items, total

def get_result_by_id(db: Session, result_id: int, user_id: Optional[int] = None) -> Optional[CCCDResult]:
    query = db.query(CCCDResult).filter(CCCDResult.id == result_id)
    if user_id:
        query = query.filter(CCCDResult.user_id == user_id)
    return query.first()

def delete_cccd_result(db: Session, result_id: int, user_id: int) -> bool:
    result = db.query(CCCDResult).filter(CCCDResult.id == result_id, CCCDResult.user_id == user_id).first()
    if not result:
        return False
    # Xóa scan_history liên kết (cascade sẽ tự động xóa result và corrections)
    if result.scan:
        db.delete(result.scan)
    else:
        db.delete(result)
    db.commit()
    return True

# ==============================================================================
# BẢNG 4: SCAN_STATISTICS (QUẢN LÝ THỐNG KÊ HỆ THỐNG)
# ==============================================================================

def get_user_statistics(db: Session, user_id: int) -> ScanStatistic:
    stat = db.query(ScanStatistic).filter(ScanStatistic.user_id == user_id).first()
    if not stat:
        stat = ScanStatistic(user_id=user_id)
        db.add(stat)
        db.commit()
        db.refresh(stat)
    return stat

def update_statistics_on_scan(
    db: Session, 
    user_id: int, 
    input_source: str, 
    confidence_score: float, 
    processing_time: float
):
    stat = get_user_statistics(db, user_id)
    stat.total_scans += 1
    if input_source == "IMAGE":
        stat.image_scans += 1
    elif input_source == "WEBCAM":
        stat.webcam_scans += 1
    elif input_source == "VIDEO":
        stat.video_scans += 1

    n = stat.total_scans
    stat.avg_confidence = round(((stat.avg_confidence * (n - 1)) + (confidence_score * 100)) / n, 2)
    stat.avg_processing_time = round(((stat.avg_processing_time * (n - 1)) + processing_time) / n, 2)
    db.commit()

# ==============================================================================
# BẢNG 5: AI_CORRECTIONS (ĐÁNH GIÁ ĐỘ ĐÚNG AI & LỊCH SỬ CHỈNH SỬA)
# ==============================================================================

def edit_cccd_result_and_record_corrections(
    db: Session,
    result_id: int,
    user_id: int,
    edit_data: CCCDResultEdit
) -> CCCDResult:
    result = db.query(CCCDResult).filter(CCCDResult.id == result_id, CCCDResult.user_id == user_id).first()
    if not result:
        raise ValueError("Không tìm thấy hồ sơ CCCD cần chỉnh sửa!")

    changed_count = 0
    for field_name, new_val in edit_data.dict(exclude_unset=True).items():
        if new_val is not None:
            old_val = getattr(result, field_name)
            str_old = str(old_val) if old_val is not None else ""
            str_new = str(new_val)

            if str_old != str_new:
                changed_count += 1
                # Ghi nhận vào BẢNG 5: ai_corrections để đánh giá độ đúng của AI
                correction = AICorrection(
                    history_id=result.history_id,
                    user_id=user_id,
                    field_name=field_name,
                    ai_prediction=str_old,
                    user_corrected=str_new,
                    is_correct=False, # AI đoán sai phải sửa lại
                    ai_confidence=result.scan.confidence_score if result.scan else 0.95
                )
                db.add(correction)
                
                # Chuyển đổi an toàn chuỗi ngày sang đối tượng date
                parsed_val = new_val
                if field_name in ("dob", "expiry_date") and isinstance(new_val, str):
                    parsed_val = parse_date_safe(new_val)

                setattr(result, field_name, parsed_val)

    if changed_count > 0:
        stat = get_user_statistics(db, user_id)
        stat.edited_scans += 1

        if result.scan:
            result.scan.status = "EDITED"
            old_conf = float(result.scan.confidence_score or 0.90)
            
            # CÀNG SỬA NHIỀU THÌ ĐỘ TIN CẬY CỦA HỒ SƠ CÀNG THẤP
            # Mỗi trường người dùng phải sửa thủ công sẽ làm giảm độ tin cậy tương ứng với tỷ lệ 1/8
            penalty_ratio = changed_count / 8.0
            new_conf = max(0.10, round(old_conf * (1.0 - penalty_ratio), 4))
            result.scan.confidence_score = new_conf

            # Cập nhật độ tin cậy trung bình của toàn hệ thống
            if stat.total_scans > 0:
                diff_percent = (new_conf - old_conf) * 100.0
                stat.avg_confidence = max(0.0, round(stat.avg_confidence + (diff_percent / stat.total_scans), 2))

        db.commit()
        db.refresh(result)

    return result

def get_all_user_corrections(db: Session, user_id: int) -> List[AICorrection]:
    return db.query(AICorrection).filter(AICorrection.user_id == user_id).order_by(desc(AICorrection.corrected_at)).all()


# ==============================================================================
# BẢNG 6: PHÂN TÍCH NHÂN KHẨU HỌC & CHẤT LƯỢNG MÔ HÌNH AI
# ==============================================================================

PROVINCES_VN = [
    "Hà Nội", "TP. Hồ Chí Minh", "Hải Phòng", "Đà Nẵng", "Cần Thơ", "An Giang",
    "Bà Rịa - Vũng Tàu", "Bắc Giang", "Bắc Kạn", "Bạc Liêu", "Bắc Ninh", "Bến Tre",
    "Bình Định", "Bình Dương", "Bình Phước", "Bình Thuận", "Cà Mau", "Cao Bằng",
    "Đắk Lắk", "Đắk Nông", "Điện Biên", "Đồng Nai", "Đồng Tháp", "Gia Lai",
    "Hà Giang", "Hà Nam", "Hà Tĩnh", "Hải Dương", "Hậu Giang", "Hòa Bình",
    "Hưng Yên", "Khánh Hòa", "Kiên Giang", "Kon Tum", "Lai Châu", "Lâm Đồng",
    "Lạng Sơn", "Lào Cai", "Long An", "Nam Định", "Nghệ An", "Ninh Bình",
    "Ninh Thuận", "Phú Thọ", "Phú Yên", "Quảng Bình", "Quảng Nam", "Quảng Ngãi",
    "Quảng Ninh", "Quảng Trị", "Sóc Trăng", "Sơn La", "Tây Ninh", "Thái Bình",
    "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế", "Tiền Giang", "Trà Vinh",
    "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc", "Yên Bái"
]

PROVINCE_ALIASES = {
    "Hà Nội": ["Hà Nội", "Ha Noi", "HN"],
    "TP. Hồ Chí Minh": ["Hồ Chí Minh", "Ho Chi Minh", "HCM", "TP.HCM", "TPHCM", "Sài Gòn", "Sai Gon"],
    "Đà Nẵng": ["Đà Nẵng", "Da Nang"],
    "Hải Phòng": ["Hải Phòng", "Hai Phong"],
    "Cần Thơ": ["Cần Thơ", "Can Tho"],
    "Bà Rịa - Vũng Tàu": ["Vũng Tàu", "Vung Tau", "Bà Rịa", "Ba Ria"],
    "Thừa Thiên Huế": ["Thừa Thiên Huế", "Thua Thien Hue", "Huế", "Hue"],
}

FIELD_MAP = [
    ("id_number", "1. Số CCCD (12 số)"),
    ("full_name", "2. Họ và tên"),
    ("dob", "3. Ngày sinh"),
    ("gender", "4. Giới tính"),
    ("nationality", "5. Quốc tịch"),
    ("origin_location", "6. Quê quán"),
    ("residence", "7. Nơi thường trú"),
    ("expiry_date", "8. Có giá trị đến"),
]


def extract_province(address_str: str) -> str:
    if not address_str:
        return "Khác"
    addr_lower = address_str.strip().lower()

    # Ưu tiên kiểm tra các alias phổ biến
    for prov, aliases in PROVINCE_ALIASES.items():
        for alias in aliases:
            if alias.lower() in addr_lower:
                return prov

    # Kiểm tra danh sách tỉnh thành chuẩn
    for prov in PROVINCES_VN:
        if prov.lower() in addr_lower:
            return prov

    return "Khác"


def get_user_demographics(db: Session, user_id: int) -> Dict[str, Any]:
    results = db.query(CCCDResult).filter(CCCDResult.user_id == user_id).all()
    total_records = len(results)

    # 1. Thống kê giới tính
    gender_counts = {"Nam": 0, "Nữ": 0, "Khác": 0}
    for r in results:
        g = str(r.gender or "").strip().lower()
        if "nam" in g:
            gender_counts["Nam"] += 1
        elif "nữ" in g or "nu" in g:
            gender_counts["Nữ"] += 1
        else:
            gender_counts["Khác"] += 1

    gender_stats = []
    for g_name, g_count in gender_counts.items():
        pct = round((g_count / total_records * 100.0), 1) if total_records > 0 else 0.0
        gender_stats.append({"name": g_name, "count": g_count, "percent": pct})

    # 2. Thống kê phân bố tỉnh thành
    province_counter: Dict[str, int] = {}
    for r in results:
        prov = extract_province(r.residence or r.origin_location or "")
        province_counter[prov] = province_counter.get(prov, 0) + 1

    # Sắp xếp tỉnh thành theo số lượng giảm dần
    sorted_provs = sorted(province_counter.items(), key=lambda x: x[1], reverse=True)
    province_stats = []
    for prov_name, p_count in sorted_provs:
        pct = round((p_count / total_records * 100.0), 1) if total_records > 0 else 0.0
        province_stats.append({"province": prov_name, "count": p_count, "percent": pct})

    # 3. Thống kê phân bố năm sinh & nhóm độ tuổi
    current_year = datetime.now().year
    age_groups = {
        "Dưới 18 tuổi": 0,
        "18 - 30 tuổi": 0,
        "31 - 45 tuổi": 0,
        "46 - 60 tuổi": 0,
        "Trên 60 tuổi": 0,
        "Chưa xác định": 0
    }

    for r in results:
        birth_year = None
        if r.dob:
            if isinstance(r.dob, (datetime, date)):
                birth_year = r.dob.year
            elif isinstance(r.dob, str):
                parts = r.dob.replace("/", "-").split("-")
                for part in parts:
                    if len(part) == 4 and part.isdigit():
                        birth_year = int(part)
                        break

        if birth_year and 1900 <= birth_year <= current_year:
            age = current_year - birth_year
            if age < 18:
                age_groups["Dưới 18 tuổi"] += 1
            elif 18 <= age <= 30:
                age_groups["18 - 30 tuổi"] += 1
            elif 31 <= age <= 45:
                age_groups["31 - 45 tuổi"] += 1
            elif 46 <= age <= 60:
                age_groups["46 - 60 tuổi"] += 1
            else:
                age_groups["Trên 60 tuổi"] += 1
        else:
            age_groups["Chưa xác định"] += 1

    age_group_stats = []
    for label, count in age_groups.items():
        pct = round((count / total_records * 100.0), 1) if total_records > 0 else 0.0
        age_group_stats.append({"label": label, "count": count, "percent": pct})

    return {
        "total_records": total_records,
        "gender_stats": gender_stats,
        "province_stats": province_stats,
        "age_group_stats": age_group_stats
    }


def get_user_ai_quality(db: Session, user_id: int) -> Dict[str, Any]:
    stat = get_user_statistics(db, user_id)
    total_scans = stat.total_scans
    edited_scans = stat.edited_scans
    perfect_scans = max(0, total_scans - edited_scans)
    perfect_rate = round((perfect_scans / total_scans * 100.0), 1) if total_scans > 0 else 100.0

    # Đếm số lỗi theo từng trường
    corrections = db.query(AICorrection).filter(AICorrection.user_id == user_id).all()
    error_counter: Dict[str, int] = {}
    for c in corrections:
        fn = c.field_name
        error_counter[fn] = error_counter.get(fn, 0) + 1

    field_accuracy = []
    for fn, label in FIELD_MAP:
        err_cnt = error_counter.get(fn, 0)
        acc_pct = max(0.0, round(100.0 - (err_cnt / total_scans * 100.0), 1)) if total_scans > 0 else 100.0
        field_accuracy.append({
            "field_name": fn,
            "field_label": label,
            "error_count": err_cnt,
            "accuracy_percent": acc_pct
        })

    return {
        "total_scans": total_scans,
        "edited_scans": edited_scans,
        "perfect_scans": perfect_scans,
        "perfect_rate": perfect_rate,
        "avg_confidence": stat.avg_confidence,
        "avg_processing_time": stat.avg_processing_time,
        "field_accuracy": field_accuracy
    }

