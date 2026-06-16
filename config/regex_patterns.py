"""
config/regex_patterns.py
========================
Regex kiểm tra dữ liệu OCR.
"""

import re
CCCD_PATTERN = re.compile(
    r"^\d{12}$"
)
DATE_PATTERN = re.compile(
    r"^\d{2}/\d{2}/\d{4}$"
)
GENDER_PATTERN = re.compile(
    r"^(Nam|Nữ)$",
    re.IGNORECASE
)
NATIONALITY_PATTERN = re.compile(
    r"^Việt Nam$",
    re.IGNORECASE
)