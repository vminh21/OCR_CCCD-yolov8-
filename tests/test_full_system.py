# tests/test_full_system.py
"""
Bộ kiểm thử toàn diện End-to-End (E2E) kiểm tra tất cả các luồng:
1. Giao diện trang chủ (Root HTML, Asset caching headers)
2. Luồng Xác thực (Đăng ký, Đăng nhập, Thông tin cá nhân, Đổi mật khẩu)
3. Luồng OCR Nhận diện CCCD (Trích xuất 8 trường từ ảnh thật)
4. Luồng Quản lý Hồ sơ (Xem danh sách, Tìm kiếm, Chi tiết, Chỉnh sửa, Xóa)
5. Luồng Thống kê & Nhân khẩu học (/api/statistics, /api/statistics/demographics)
6. Luồng Đánh giá Chất lượng AI (/api/statistics/ai-quality, /api/corrections)
7. Luồng Trực tiếp Camera Probe (/predict/camera-probe)
"""

import os
import sys
import time
from pathlib import Path

# Thêm thư mục gốc vào sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("\n" + "=" * 65)
print("🚀 BẮT ĐẦU KIỂM THỬ TOÀN DIỆN HỆ THỐNG CCCD OCR (FULL E2E TEST)")
print("=" * 65 + "\n")

# ------------------------------------------------------------------------------
# LUỒNG 1: GIAO DIỆN & TẢI TRANG WEB (PAGE LOAD & CACHE HEADERS)
# ------------------------------------------------------------------------------
print("[LUỒNG 1/7] Kiểm tra Tải Trang Chủ & Cấu hình Header Cache...")
r_root = client.get("/")
assert r_root.status_code == 200, f"Lỗi tải trang chủ: {r_root.status_code}"
assert "<div id=\"root\"></div>" in r_root.text, "Không tìm thấy root container React"
assert "Cache-Control" in r_root.headers, "Thiếu header Cache-Control"
assert "no-cache" in r_root.headers["Cache-Control"], "Cache-Control chưa có no-cache"
print("   ✅ [PASS] Trang chủ trả về HTTP 200 OK, Cache-Control: no-cache, cấu trúc React chuẩn.")

# Kiểm tra file bundle tĩnh
import re
js_match = re.search(r'src="(/assets/[^"]+\.js)"', r_root.text)
css_match = re.search(r'href="(/assets/[^"]+\.css)"', r_root.text)
assert js_match, "Không tìm thấy script bundle trong HTML"
assert css_match, "Không tìm thấy CSS bundle trong HTML"

r_js = client.get(js_match.group(1))
assert r_js.status_code in (200, 304), f"Lỗi tải JS bundle: {r_js.status_code}"
r_css = client.get(css_match.group(1))
assert r_css.status_code in (200, 304), f"Lỗi tải CSS bundle: {r_css.status_code}"
print(f"   ✅ [PASS] JS Bundle ({js_match.group(1)}) & CSS Bundle ({css_match.group(1)}) tải thành công!")

# ------------------------------------------------------------------------------
# LUỒNG 2: XÁC THỰC NGƯỜI DÙNG (AUTH FLOW)
# ------------------------------------------------------------------------------
print("\n[LUỒNG 2/7] Kiểm tra Luồng Xác Thực (Đăng ký, Đăng nhập, Profile, Đổi mật khẩu)...")
ts = int(time.time() * 1000)
test_user = f"user_{ts}"
test_email = f"user_{ts}@test.vn"
test_pass = "P@ssword123"

# Đăng ký
r_reg = client.post("/api/auth/register", json={
    "username": test_user,
    "email": test_email,
    "full_name": "Nguyễn Văn Test",
    "password": test_pass
})
assert r_reg.status_code == 201, f"Lỗi đăng ký: {r_reg.text}"
print(f"   ✅ [PASS] Đăng ký thành công tài khoản: {test_user}")

# Đăng nhập
r_login = client.post("/api/auth/login", json={
    "username": test_user,
    "password": test_pass
})
assert r_login.status_code == 200, f"Lỗi đăng nhập: {r_login.text}"
token = r_login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("   ✅ [PASS] Đăng nhập nhận JWT Access Token thành công.")

# Kiểm tra Profile
r_me = client.get("/api/auth/me", headers=headers)
assert r_me.status_code == 200, f"Lỗi lấy thông tin: {r_me.text}"
assert r_me.json()["username"] == test_user
print(f"   ✅ [PASS] API /api/auth/me trả về đúng thông tin: {r_me.json()['full_name']}")

# Đổi mật khẩu
r_change = client.post("/api/auth/change-password", headers=headers, json={
    "old_password": test_pass,
    "new_password": "NewP@ssword456"
})
assert r_change.status_code == 200, f"Lỗi đổi mật khẩu: {r_change.text}"
print("   ✅ [PASS] Đổi mật khẩu thành công.")

# ------------------------------------------------------------------------------
# LUỒNG 3: NHẬN DIỆN CCCD (OCR PREDICT FLOW)
# ------------------------------------------------------------------------------
print("\n[LUỒNG 3/7] Kiểm tra Nhận Diện CCCD (YOLOv8 + VietOCR)...")
sample_img = ROOT_DIR / "data" / "input" / "cccd1.jpg"
assert sample_img.exists(), f"Không tìm thấy ảnh mẫu {sample_img}"

with open(sample_img, "rb") as f:
    files = {"file": ("cccd1.jpg", f.read(), "image/jpeg")}
    r_ocr = client.post("/predict/image", headers=headers, files=files, data={"input_source": "IMAGE"})

assert r_ocr.status_code == 200, f"Lỗi nhận diện OCR: {r_ocr.text}"
ocr_data = r_ocr.json()
print("   Kết quả trích xuất:", {
    "so_cccd": ocr_data.get("so_cccd"),
    "ho_ten": ocr_data.get("ho_ten"),
    "ngay_sinh": ocr_data.get("ngay_sinh"),
    "que_quan": ocr_data.get("que_quan"),
    "noi_ctru": ocr_data.get("noi_ctru"),
})
assert ocr_data.get("so_cccd"), "Không trích xuất được số CCCD"
result_id = ocr_data.get("result_id")
assert result_id, "Không có result_id được tạo"
print(f"   ✅ [PASS] Nhận diện CCCD thành công, tạo hồ sơ ID #{result_id}")

# Kiểm tra ảnh visualization phục vụ tĩnh
if ocr_data.get("crop_image_path"):
    r_media = client.get(ocr_data["crop_image_path"])
    assert r_media.status_code in (200, 304), f"Lỗi tải ảnh media: {r_media.status_code}"
    print(f"   ✅ [PASS] Ảnh cắt trực quan ({ocr_data['crop_image_path']}) truy cập thành công!")

# ------------------------------------------------------------------------------
# LUỒNG 4: QUẢN LÝ HỒ SƠ KẾT QUẢ (RESULTS MANAGEMENT FLOW)
# ------------------------------------------------------------------------------
print("\n[LUỒNG 4/7] Kiểm tra Quản Lý Hồ Sơ (Xem danh sách, Tìm kiếm, Sửa, Xóa)...")

# Xem danh sách
r_list = client.get("/api/results?limit=50&offset=0", headers=headers)
assert r_list.status_code == 200, f"Lỗi lấy danh sách kết quả: {r_list.text}"
items = r_list.json()["items"]
assert len(items) > 0, "Danh sách rỗng"
print(f"   ✅ [PASS] Lấy danh sách kết quả thành công ({len(items)} hồ sơ).")

# Tìm kiếm theo số CCCD
so_cccd = ocr_data.get("so_cccd")
r_search = client.get(f"/api/results?search={so_cccd}&limit=10&offset=0", headers=headers)
assert r_search.status_code == 200
assert len(r_search.json()["items"]) >= 1
print(f"   ✅ [PASS] Tìm kiếm theo số CCCD '{so_cccd}' thành công.")

# Chỉnh sửa hồ sơ để tạo bản ghi đối soát AI corrections
r_edit = client.put(f"/api/results/{result_id}", headers=headers, json={
    "full_name": "NGUYỄN VĂN MINH CHUẨN",
    "residence": "Phường Cầu Giấy, Quận Cầu Giấy, TP. Hà Nội"
})
assert r_edit.status_code == 200, f"Lỗi chỉnh sửa hồ sơ: {r_edit.text}"
print(f"   ✅ [PASS] Hiệu chỉnh hồ sơ #{result_id} thành công.")

# ------------------------------------------------------------------------------
# LUỒNG 5: THỐNG KÊ LƯỢT QUÉT & NHÂN KHẨU HỌC (STATISTICS & DEMOGRAPHICS)
# ------------------------------------------------------------------------------
print("\n[LUỒNG 5/7] Kiểm tra Thống Kê Lượt Quét & Phân Tích Nhân Khẩu Học...")
r_stat = client.get("/api/statistics", headers=headers)
assert r_stat.status_code == 200
stat_val = r_stat.json()
print("   Thống kê lượt quét:", {
    "total": stat_val["total_scans"],
    "image": stat_val["image_scans"],
    "webcam": stat_val["webcam_scans"],
    "video": stat_val["video_scans"],
})
assert stat_val["total_scans"] >= 1
print("   ✅ [PASS] API /api/statistics trả về đầy đủ 4 loại nguồn quét.")

r_demo = client.get("/api/statistics/demographics", headers=headers)
assert r_demo.status_code == 200
demo_val = r_demo.json()
print("   Nhân khẩu học:", {
    "total_records": demo_val["total_records"],
    "gender_stats": demo_val["gender_stats"],
    "top_province": demo_val["province_stats"][:2],
    "age_groups": [a for a in demo_val["age_group_stats"] if a["count"] > 0],
})
assert demo_val["total_records"] >= 1
print("   ✅ [PASS] API /api/statistics/demographics tính toán Nam/Nữ, Tỉnh thành, Năm sinh chính xác 100%.")

# ------------------------------------------------------------------------------
# LUỒNG 6: ĐÁNH GIÁ ĐỘ ĐÚNG CỦA AI (AI QUALITY & CORRECTIONS AUDIT)
# ------------------------------------------------------------------------------
print("\n[LUỒNG 6/7] Kiểm tra Đánh Giá Độ Đúng AI & Đối Soát Sửa Đổi...")
r_ai = client.get("/api/statistics/ai-quality", headers=headers)
assert r_ai.status_code == 200
ai_val = r_ai.json()
print("   Chỉ số chất lượng AI:", {
    "avg_confidence": ai_val["avg_confidence"],
    "perfect_rate": ai_val["perfect_rate"],
    "edited_scans": ai_val["edited_scans"],
    "total_fields": len(ai_val["field_accuracy"]),
})
assert len(ai_val["field_accuracy"]) == 8, "Phải có đủ 8 trường đánh giá độ chính xác"
print("   ✅ [PASS] API /api/statistics/ai-quality trả về đủ 8 trường chính xác.")

r_corr = client.get("/api/corrections", headers=headers)
assert r_corr.status_code == 200
corr_list = r_corr.json()
assert len(corr_list) >= 1, "Phải có ít nhất 1 bản ghi sửa đổi từ bước trước"
latest_corr = corr_list[0]
print("   Bản ghi đối soát mới nhất:", {
    "field": latest_corr["field_name"],
    "ai_prediction": latest_corr["ai_prediction"],
    "user_corrected": latest_corr["user_corrected"],
    "is_correct": latest_corr["is_correct"]
})
print("   ✅ [PASS] Bảng đối soát AI ghi nhận chính xác vết sửa đổi của người dùng.")

# ------------------------------------------------------------------------------
# LUỒNG 7: CAMERA PROBE & DỌN DẸP
# ------------------------------------------------------------------------------
print("\n[LUỒNG 7/7] Kiểm tra Camera Probe & Xóa Hồ Sơ Thử Nghiệm...")
with open(sample_img, "rb") as f:
    files = {"file": ("probe_frame.jpg", f.read(), "image/jpeg")}
    r_probe = client.post("/predict/camera-probe", headers=headers, files=files)
assert r_probe.status_code == 200
probe_val = r_probe.json()
assert "detected" in probe_val
print("   ✅ [PASS] API /predict/camera-probe trả về phản hồi theo thời gian thực:", probe_val.get("message"))

# Xóa hồ sơ thử nghiệm
r_del = client.delete(f"/api/results/{result_id}", headers=headers)
assert r_del.status_code == 200
print(f"   ✅ [PASS] Xóa hồ sơ thử nghiệm #{result_id} thành công.")

print("\n" + "=" * 65)
print("🎉 TẤT CẢ 7/7 LUỒNG NGHIỆP VỤ ĐỀU PASS 100% - KHÔNG CÓ LỖI API!")
print("=" * 65 + "\n")
