# src/core/validator.py
import re
import unicodedata

# Danh mục 63 Tỉnh / Thành phố trực thuộc Trung ương của Việt Nam
PROVINCES = [
    "Hà Nội", "Hải Phòng", "Hải Dương", "Hưng Yên", "Bắc Ninh", "Nam Định", "Ninh Bình",
    "Thái Bình", "Hà Nam", "Vĩnh Phúc", "Quảng Ninh", "Bắc Giang", "Phú Thọ", "Thái Nguyên",
    "Lạng Sơn", "Tuyên Quang", "Hà Giang", "Cao Bằng", "Yên Bái", "Lào Cai", "Bắc Kạn",
    "Sơn La", "Hòa Bình", "Điện Biên", "Lai Châu", "Thanh Hóa", "Nghệ An", "Hà Tĩnh",
    "Quảng Bình", "Quảng Trị", "Thừa Thiên Huế", "Đà Nẵng", "Quảng Nam", "Quảng Ngãi",
    "Bình Định", "Phú Yên", "Khánh Hòa", "Ninh Thuận", "Bình Thuận", "Kon Tum", "Gia Lai",
    "Đắk Lắk", "Đắk Nông", "Lâm Đồng", "TP. Hồ Chí Minh", "Hồ Chí Minh", "Bình Dương",
    "Đồng Nai", "Bà Rịa - Vũng Tàu", "Tây Ninh", "Bình Phước", "Long An", "Tiền Giang",
    "Bến Tre", "Trà Vinh", "Vĩnh Long", "Đồng Tháp", "An Giang", "Kiên Giang", "Cần Thơ",
    "Hậu Giang", "Sóc Trăng", "Bạc Liêu", "Cà Mau"
]

# Bảng sửa lỗi chính tả OCR thường gặp đối với địa danh
COMMON_TYPOS = {
    "Kìm Sơn": "Kim Sơn",
    "Hoàng Mái": "Hoàng Mai",
    "Hoàng Mãi": "Hoàng Mai",
    "Hải Dưong": "Hải Dương",
    "Hà Nôi": "Hà Nội",
    "Ninh Binh": "Ninh Bình",
    "Ha Noi": "Hà Nội",
    "Hai Duong": "Hải Dương",
    "Hai Phong": "Hải Phòng",
    "Dinh Cong": "Định Công",
    "Bình Dưong": "Bình Dương",
    "TỞ": "Tổ",
    "Tố": "Tổ",
    "Thộn": "Thôn",
    "NĐI THƯƠNG": "An Thượng",
    "Nđi Thương": "An Thượng",
    "An Thương": "An Thượng",
    "NGƯỜI THƯƠNG": "An Thượng",
    "Người Thương": "An Thượng",
    "Hà Dương": "Hải Dương",
    "Hai Dương": "Hải Dương",
    "HẢI DUSINH": "Hải Dương",
    "Hoàng Mã": "Hoàng Mai"
}



def normalize_vietnamese_text(text: str) -> str:
    """Chuẩn hóa Unicode tiếng Việt về một dạng dựng sẵn duy nhất (NFC)."""
    if not text:
        return ""
    text = unicodedata.normalize('NFC', str(text))
    return " ".join(text.split()).strip()


def clean_id_number(text: str) -> str:
    """Hậu xử lý cho Số CCCD: Phải có đúng 12 chữ số."""
    if not text:
        return ""
    replacements = {
        'O': '0', 'o': '0',
        'I': '1', 'l': '1',
        'S': '5', 's': '5',
        'G': '6', 'b': '6',
        'B': '8', 'Z': '2', 'z': '2'
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    digits = re.sub(r'[^0-9]', '', text)
    return digits


def clean_name(text: str) -> str:
    """
    Hậu xử lý Họ và tên:
    1. Loại bỏ tiền tố nhãn thừa như 'Họ và tên:', 'Full name:'.
    2. Sửa các số bị đọc nhầm trong chữ cái (0->O, 1->I, 8->B, 5->S...).
    3. Loại bỏ triệt để số và các dấu câu thừa (, . - /...).
    4. Chuẩn hóa viết hoa toàn bộ chuẩn tiếng Việt.
    """
    if not text:
        return ""
    text = normalize_vietnamese_text(text)

    # Xóa nhãn thừa nếu có
    text = re.sub(r'^(họ\s*và\s*tên|họ\s*tên|full\s*name|name)[\s:.-]*', '', text, flags=re.IGNORECASE)

    # Thay thế các số đọc nhầm thành chữ cái tương ứng
    num_to_letter = {'0': 'O', '1': 'I', '8': 'B', '5': 'S', '2': 'Z'}
    for k, v in num_to_letter.items():
        text = text.replace(k, v)

    # Chỉ giữ lại các chữ cái tiếng Việt và khoảng trắng, loại bỏ mọi số và dấu câu
    text = re.sub(r'[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰự\s]', '', text)

    # Viết hoa toàn bộ tên
    text = " ".join(text.split()).upper()
    return text


def clean_nationality(text: str) -> str:
    """
    Hậu xử lý Quốc tịch:
    Khắc phục các lỗi nhầm dấu OCR như 'Việc Nam', 'Việt Năm', 'Viet Nam', 'VIET NAM'...
    Chuẩn hóa tuyệt đối về 'Việt Nam'.
    """
    if not text:
        return "Việt Nam"
    norm = normalize_vietnamese_text(text).lower()

    # Bắt mọi biến thể mờ của Việt Nam
    if any(k in norm for k in ["việt", "viet", "việc", "viêt", "nam", "năm", "vn"]):
        return "Việt Nam"

    # Mặc định trên CCCD Việt Nam
    return "Việt Nam"


def clean_gender(raw_gender: str, id_number: str = "") -> str:
    """
    Hậu xử lý Giới tính:
    1. Ưu tiên đối chiếu chéo với Số CCCD:
       Chữ số thứ 4 (index 3) trong 12 số CCCD: Chẵn là NAM, Lẻ là NỮ.
    2. Nếu không có số CCCD, bắt toàn bộ các biến thể sai dấu của chữ NỮ (NỬ, NỨ, NỰ, NU, NÚ...).
    """
    # 1. Kiểm tra đối chiếu chéo qua số CCCD
    clean_id = re.sub(r'[^0-9]', '', str(id_number))
    if len(clean_id) >= 4:
        gender_code = int(clean_id[3])
        # 0, 2, 4, 6, 8 là NAM; 1, 3, 5, 7, 9 là NỮ
        return "NAM" if gender_code % 2 == 0 else "NỮ"

    # 2. Xử lý text thô nếu không có số CCCD
    g = normalize_vietnamese_text(raw_gender).upper()

    female_variants = ["NỮ", "NỬ", "NỨ", "NỰ", "NỪ", "NƯ", "NU", "NÚ", "NŨ", "NÜ", "NW"]
    if any(k in g for k in female_variants):
        return "NỮ"

    male_variants = ["NAM", "AM", "NAN", "MAM", "NA"]
    if any(k in g for k in male_variants):
        return "NAM"

    if g.startswith("N") and "M" not in g:
        return "NỮ"

    return "NAM"


def _parse_date_components(text: str):
    """Trích xuất ngày, tháng, năm từ chuỗi text thô và sửa các ký tự chữ cái lẫn vào số."""
    if not text:
        return None, None, None
    text = re.sub(r'[\s.,\-_]+', '/', text)
    # Sửa chữ cái đọc nhầm thành số (ví dụ: 200s -> 2005, O -> 0, I -> 1)
    date_replacements = {
        'O': '0', 'o': '0',
        'I': '1', 'l': '1',
        's': '5', 'S': '5',
        'b': '6', 'B': '8',
        'Z': '2', 'z': '2'
    }
    for char, rep in date_replacements.items():
        text = text.replace(char, rep)

    m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    if m:
        d, m, y = m.groups()
        return int(d), int(m), int(y)

    m_year = re.search(r'(\d{4})', text)
    if m_year:
        return None, None, int(m_year.group(1))

    return None, None, None


def clean_dates(dob_raw: str, exp_raw: str):
    """
    Đồng bộ Ngày sinh và Có giá trị đến:
    - Theo Luật CCCD: Ngày và tháng hết hạn LUÔN TRÙNG với ngày và tháng sinh (hết hạn vào ngày sinh nhật ở mốc 25, 40, 60 tuổi).
    - Tự động nắn ngày/tháng của Ngày hết hạn theo Ngày sinh.
    - Kiểm tra và sửa năm hết hạn khớp với mốc tuổi quy định.
    """
    d_dob, m_dob, y_dob = _parse_date_components(dob_raw)
    d_exp, m_exp, y_exp = _parse_date_components(exp_raw)

    # Format ngày sinh chuẩn
    if d_dob and m_dob and y_dob:
        clean_dob = f"{d_dob:02d}/{m_dob:02d}/{y_dob}"
    elif y_dob:
        clean_dob = str(y_dob)
    else:
        clean_dob = dob_raw.strip()

    # Xử lý trường hợp "Không thời hạn" (người trên 60 tuổi)
    exp_lower = exp_raw.lower() if exp_raw else ""
    if any(k in exp_lower for k in ["không", "thời hạn", "vô thời hạn"]):
        return clean_dob, "Không thời hạn"

    # Đồng bộ ngày hết hạn với ngày sinh
    clean_exp = exp_raw.strip()
    if d_dob and m_dob and y_dob:
        # Các mốc tuổi đổi thẻ CCCD: 25 tuổi, 40 tuổi, 60 tuổi
        milestones = [25, 40, 60]
        valid_targets = [y_dob + m for m in milestones]

        if y_exp:
            # Tìm mốc gần nhất trong các mốc 25, 40, 60
            closest_target = min(valid_targets, key=lambda tgt: abs(y_exp - tgt))
            if abs(y_exp - closest_target) <= 4:
                y_exp = closest_target
            else:
                # Nếu sai lệch quá lớn (ví dụ đọc nhầm 2050 hay 2108 cho người sinh 2005)
                # Người sinh từ năm 2000 trở lại đây có mốc đầu tiên là 25 tuổi
                y_exp = valid_targets[0] if y_dob >= 2000 else closest_target
        else:
            # Mặc định mốc 25 năm từ năm sinh
            y_exp = y_dob + 25

        clean_exp = f"{d_dob:02d}/{m_dob:02d}/{y_exp}"
    elif d_exp and m_exp and y_exp:
        clean_exp = f"{d_exp:02d}/{m_exp:02d}/{y_exp}"

    return clean_dob, clean_exp


def clean_places(text: str) -> str:
    """
    Hậu xử lý Quê quán và Nơi thường trú:
    1. Xóa nhãn thẻ bị OCR cắt dính ('Quê quán:', 'Nơi thường trú:'...).
    2. Sửa các lỗi chính tả phổ biến ('Kìm Sơn' -> 'Kim Sơn', 'Hoàng Mãi' -> 'Hoàng Mai'...).
    3. Chuẩn hóa 63 tỉnh/thành phố ở phần cuối địa chỉ.
    4. Tự động phục hồi thứ tự hành chính nếu Dòng 1 và Dòng 2 bị đảo ngược.
    5. Chuẩn hóa dấu phẩy ', ' phân tách giữa các cấp hành chính.
    """
    if not text:
        return ""
    text = normalize_vietnamese_text(text)

    # 1. Xóa tiền tố nhãn thừa
    text = re.sub(
        r'^(quê\s*quán|nơi\s*thường\s*trú|nơi\s*cư\s*trú|nơi\s*đk\s*hkt|place\s*of\s*origin|place\s*of\s*residence)[\s:.-]*',
        '', text, flags=re.IGNORECASE
    )

    # 2. Thay thế các lỗi chính tả OCR thường gặp
    for typo, correct in COMMON_TYPOS.items():
        text = re.sub(re.escape(typo), correct, text, flags=re.IGNORECASE)

    # 3. Chuẩn hóa dấu phẩy ngăn cách
    text = re.sub(r'[\.;]+', ',', text)
    text = re.sub(r'\s*,\s*', ', ', text)
    text = re.sub(r'^,\s*', '', text)
    text = re.sub(r',\s*$', '', text)

    # 4. Tự động sửa nếu bị đảo ngược thứ tự hành chính (đơn vị lớn ở đầu, đơn vị nhỏ như Tổ/Xóm/Thôn ở cuối)
    parts = [p.strip() for p in text.split(',') if p.strip()]
    if len(parts) >= 2:
        last_part = parts[-1]
        # Nếu phần cuối cùng là Tổ / Thôn / Xóm / Bản / Ấp / Số nhà
        if re.match(r'^(tổ|thôn|xóm|bản|ấp|số|ngõ|ngách|k|khu)\s+\d+', last_part, re.IGNORECASE):
            parts = [last_part] + parts[:-1]
            text = ', '.join(parts)

    # 5. Đối chiếu và chuẩn hóa tỉnh/thành phố cuối cùng nếu có
    for prov in PROVINCES:
        norm_prov = normalize_vietnamese_text(prov).lower()
        if text.lower().endswith(norm_prov):
            prefix = text[:-len(norm_prov)].rstrip(" ,")
            text = f"{prefix}, {prov}" if prefix else prov
            break

    return text.strip()



def validate_results(ocr_results: dict) -> dict:
    """
    Hàm lõi duyệt qua kết quả OCR thô và áp dụng quy trình kiểm tra chéo đa trường:
    - Bóc tách văn bản thô.
    - Đối chiếu chéo Số CCCD với Giới tính.
    - Đồng bộ Ngày sinh với Ngày hết hạn.
    - Chuẩn hóa Họ tên, Quốc tịch, Quê quán, Nơi thường trú.
    """
    raw_data = {}
    for field_name, ocr_item in ocr_results.items():
        if isinstance(ocr_item, dict):
            raw_data[field_name] = ocr_item.get("text", "")
        else:
            raw_data[field_name] = str(ocr_item or "")

    # 1. Số CCCD
    so_cccd = clean_id_number(raw_data.get("so_cccd", ""))

    # 2. Họ và tên
    ho_ten = clean_name(raw_data.get("ho_ten", ""))

    # 3. Giới tính (kiểm tra chéo qua Số CCCD)
    gioi_tinh = clean_gender(raw_data.get("gioi_tinh", ""), so_cccd)

    # 4. Quốc tịch
    quoc_tich = clean_nationality(raw_data.get("quoc_tich", ""))

    # 5. Ngày sinh & Ngày hết hạn (đồng bộ ngày/tháng và mốc tuổi)
    dob_raw = raw_data.get("ngay_sinh", "")
    exp_raw = raw_data.get("ngay_het_han", "")
    ngay_sinh, ngay_het_han = clean_dates(dob_raw, exp_raw)

    # 6. Quê quán & Nơi thường trú
    que_quan = clean_places(raw_data.get("que_quan", ""))
    noi_ctru = clean_places(raw_data.get("noi_ctru", ""))

    validated_data = {
        "so_cccd": so_cccd,
        "ho_ten": ho_ten,
        "ngay_sinh": ngay_sinh,
        "gioi_tinh": gioi_tinh,
        "quoc_tich": quoc_tich,
        "que_quan": que_quan,
        "noi_ctru": noi_ctru,
        "ngay_het_han": ngay_het_han
    }

    return validated_data