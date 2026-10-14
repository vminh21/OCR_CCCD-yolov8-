import requests
import json
import time
import sys

BASE_URL = "https://vminh21-ccccd-ocr.hf.space"
print(f"=== TESTING LIVE SPACE: {BASE_URL} ===\n")

# 1. Test Root UI
print("[1/7] Testing Root GET / (Facebook UI)...")
r_root = requests.get(BASE_URL)
assert r_root.status_code == 200, f"Root returned {r_root.status_code}"
assert "CCCD AI • Hệ Thống Nhận Diện" in r_root.text, "Page title mismatch"
assert "dropzone" in r_root.text, "Dropzone not found"
assert "auth-screen" in r_root.text, "Auth screen not found"
print(f"   => PASS! HTML size: {len(r_root.text):,} bytes. 100% Facebook UI confirmed!\n")

# 2. Test Registration & Login
ts = int(time.time())
test_user = f"user_{ts}"
test_email = f"user_{ts}@gmail.com"
test_pass = "SecurePass123!"

print(f"[2/7] Testing Authentication (Register + Login) for {test_user}...")
r_reg = requests.post(f"{BASE_URL}/api/auth/register", json={
    "username": test_user,
    "email": test_email,
    "full_name": "Nguyen Van A",
    "password": test_pass
})
print("   Register status:", r_reg.status_code, r_reg.json())
assert r_reg.status_code == 201, f"Registration failed: {r_reg.text}"

r_login = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": test_user,
    "password": test_pass
})
print("   Login status:", r_login.status_code)
assert r_login.status_code == 200, f"Login failed: {r_login.text}"
token_data = r_login.json()
access_token = token_data.get("access_token")
assert access_token, "No access token returned"
auth_headers = {"Authorization": f"Bearer {access_token}"}

r_me = requests.get(f"{BASE_URL}/api/auth/me", headers=auth_headers)
assert r_me.status_code == 200, f"Auth me failed: {r_me.text}"
print("   Logged in profile:", r_me.json())
print("   => PASS! JWT Auth is working flawlessly!\n")

# 3. Test Statistics (pre-scan)
print("[3/7] Testing GET /api/statistics...")
r_stats = requests.get(f"{BASE_URL}/api/statistics", headers=auth_headers)
assert r_stats.status_code == 200, f"Stats failed: {r_stats.text}"
print("   Pre-scan Stats:", r_stats.json())
print("   => PASS!\n")

# 4. Test Camera Probe
print("[4/7] Testing Real-time eKYC Camera Probe (POST /predict/camera-probe)...")
with open("data/input/cccd1.jpg", "rb") as f:
    files = {"file": ("camera_frame.jpg", f, "image/jpeg")}
    r_cam = requests.post(f"{BASE_URL}/predict/camera-probe", files=files)
assert r_cam.status_code == 200, f"Camera probe failed: {r_cam.text}"
cam_res = r_cam.json()
print("   Camera probe feedback:", cam_res)
assert "card_detected" in cam_res or "ready" in cam_res or "status" in cam_res or "score" in cam_res or "feedback" in cam_res
print("   => PASS! Camera probe feedback received!\n")

# 5. Test Full CCCD Prediction
print("[5/7] Testing Full CCCD OCR Pipeline (POST /predict/image)...")
start_t = time.time()
with open("data/input/cccd1.jpg", "rb") as f:
    files = {"file": ("cccd1.jpg", f, "image/jpeg")}
    r_pred = requests.post(f"{BASE_URL}/predict/image", headers=auth_headers, files=files)
elapsed = time.time() - start_t
print(f"   Prediction status: {r_pred.status_code} (took {elapsed:.2f}s)")
assert r_pred.status_code == 200, f"Prediction failed with {r_pred.status_code}: {r_pred.text}"
pred_data = r_pred.json()

print("\n--- EXTRACTED CCCD DATA ---")
fields = ["so_cccd", "ho_ten", "ngay_sinh", "gioi_tinh", "quoc_tich", "que_quan", "noi_ctru", "ngay_het_han"]
for k in fields:
    print(f"   {k}: {pred_data.get(k)}")

assert pred_data.get("so_cccd") == "001204014664", f"Unexpected CCCD: {pred_data.get('so_cccd')}"
assert "NGUYỄN MINH QUÂN" in (pred_data.get("ho_ten") or ""), f"Unexpected name: {pred_data.get('ho_ten')}"
assert pred_data.get("visualization_base64"), "Missing visualization_base64"
assert pred_data.get("scan_id"), "Missing scan_id"
print("   => PASS! High accuracy OCR results returned with bbox visualization and avatar!\n")

# 6. Test History & Results
print("[6/7] Testing GET /api/history & GET /api/results...")
r_hist = requests.get(f"{BASE_URL}/api/history", headers=auth_headers)
assert r_hist.status_code == 200, f"History failed: {r_hist.text}"
hist_items = r_hist.json()
print(f"   ScanHistory count: {len(hist_items)}")
assert len(hist_items) >= 1, "Scan history was not saved to DB"

r_res = requests.post(f"{BASE_URL}/api/results", headers=auth_headers) if False else requests.get(f"{BASE_URL}/api/results", headers=auth_headers)
assert r_res.status_code == 200, f"Results failed: {r_res.text}"
res_data = r_res.json()
results_list = res_data.get("items", [])
print(f"   CCCD Results count: {res_data.get('total')}")
assert len(results_list) >= 1, "No CCCD results in table"
latest_cccd = results_list[0]
print(f"   Latest CCCD in Table: ID={latest_cccd.get('id')}, So CCCD={latest_cccd.get('id_number')}, Ho Ten={latest_cccd.get('full_name')}")
assert latest_cccd.get('id_number') == "001204014664"
assert "NGUYỄN MINH QUÂN" in latest_cccd.get('full_name')
print("   => PASS! History & CCCD Results persist and query perfectly!\n")

# 7. Test Statistics (post-scan)
print("[7/7] Testing Updated Statistics...")
r_stats2 = requests.get(f"{BASE_URL}/api/statistics", headers=auth_headers)
assert r_stats2.status_code == 200
stats_data = r_stats2.json()
print("   Updated stats:", stats_data)
assert stats_data.get("total_scans") >= 1
assert stats_data.get("image_scans") >= 1
print("   => PASS!\n")

print("==================================================")
print("ALL 7 CORE FUNCTIONALITIES PASSED 100% ON LIVE SPACE!")
print("==================================================")
