import re

from config.regex_patterns import (
    CCCD_PATTERN,
    DATE_PATTERN
)

OCR_FIX_MAP = {
    "O": "0",
    "o": "0",
    "I": "1",
    "l": "1",
    "S": "5",
    "B": "8",
    "|": "1"
}

def clean_text(text):
    if text is None:
        return ""
    text = text.strip()
    text = re.sub(
        r"\s+",
        " ",
        text
    )
    return text

def fix_numeric_ocr(text):
    result = ""
    for c in text:
        if c in OCR_FIX_MAP:
            result += OCR_FIX_MAP[c]
        else:
            result += c
    return result

def validate_cccd(text):
    text = clean_text(text)
    text = fix_numeric_ocr(text)
    text = re.sub(
        r"\D",
        "",
        text
    )
    if len(text) != 12:
        return ""
    if re.match(
        CCCD_PATTERN,
        text
    ):
        return text
    return ""

def validate_date(text):
    text = clean_text(text)
    text = fix_numeric_ocr(text)
    text = text.replace("-", "/")
    text = text.replace(".", "/")
    m = re.search(
        r"(\d{2}/\d{2}/\d{4})",
        text
    )
    if not m:
        return ""
    date_text = m.group(1)
    if re.match(
        DATE_PATTERN,
        date_text
    ):
        return date_text
    return ""

def validate_gender(text):
    text = clean_text(text).upper()
    if "NAM" in text:
        return "Nam"
    if "NỮ" in text:
        return "Nữ"
    if "NU" in text:
        return "Nữ"
    return text

def validate_nationality(text):
    text = clean_text(text).upper()
    if "VIỆT" in text:
        return "Việt Nam"
    if "VIET" in text:
        return "Việt Nam"
    return text

def validate_name(text):
    text = clean_text(text)
    text = text.upper()
    return text

def validate_address(text):
    text = clean_text(text)
    return text

def validate_field(
    field_name,
    text
):
    if field_name == "so_cccd":
        return validate_cccd(text)
    elif field_name == "ngay_sinh":
        return validate_date(text)
    elif field_name == "ngay_het_han":
        return validate_date(text)
    elif field_name == "gioi_tinh":
        return validate_gender(text)
    elif field_name == "quoc_tich":
        return validate_nationality(text)
    elif field_name == "ho_ten":
        return validate_name(text)
    elif field_name == "que_quan":
        return validate_address(text)
    elif field_name == "noi_ctru":
        return validate_address(text)
    return clean_text(text)

def validate_results(ocr_results):
    """
    Input:
    {
        "so_cccd": {
            "text": "...",
            "confidence": ...
        }
    }
    """
    final_data = {}
    for field_name, info in ocr_results.items():
        raw_text = info["text"]
        final_data[field_name] = validate_field(
            field_name,
            raw_text
        )
    return final_data