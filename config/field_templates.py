# config/field_templates.py

# Tọa độ cắt ảnh đại diện (Avatar) - Định dạng: (x, y, width, height) theo tỷ lệ %
AVATAR_COORDS = (0.05, 0.35, 0.22, 0.35) 

# Tọa độ cắt các trường thông tin mặt trước CCCD
# Định dạng: "tên_trường": (x, y, width, height) theo tỷ lệ phần trăm (0.0 -> 1.0)
CCCD_FRONT_FIELDS = {
    "so_cccd": (0.45, 0.45, 0.45, 0.05),
    "ho_ten": (0.28, 0.54, 0.65, 0.05),
    "ngay_sinh": (0.55, 0.60, 0.25, 0.05),
    "gioi_tinh": (0.42, 0.67, 0.08, 0.04),
    "quoc_tich": (0.76, 0.67, 0.20, 0.04),
    "que_quan": (0.28, 0.74, 0.68, 0.05),
    "noi_ctru": (0.28, 0.82, 0.68, 0.08),
    "ngay_het_han": (0.12, 0.88, 0.20, 0.05)
}

# Bộ lọc ký tự (Whitelist) cho từng trường để tăng độ chính xác cho OCR
FIELD_WHITELIST = {
    "so_cccd": "0123456789",
    "ngay_sinh": "0123456789/",
    "ngay_het_han": "0123456789/",
    "gioi_tinh": "NamNữ",
    "quoc_tich": "ViệtNam ",
    "ho_ten": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰự ",
    "que_quan": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰự0123456789, -",
    "noi_ctru": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰự0123456789, -/"
}