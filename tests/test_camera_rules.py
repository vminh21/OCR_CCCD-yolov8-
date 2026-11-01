# tests/test_camera_rules.py
"""
Bộ kiểm thử quy tắc Camera AI (Camera Rules Test):
1. Nhận diện mặt trước CCCD: Cho phép chụp (can_capture=True, color='green', side='front')
2. Nhận diện mặt sau CCCD: Báo rõ "Đây là mặt sau của CCCD", không chụp tự động
3. Từ chối thẻ khác (Thẻ sinh viên, thẻ ngân hàng...): Báo đỏ (color='red', side='invalid_card', can_capture=False)
4. Chốt chặn bảo vệ API /predict/image: Chặn thẻ khác và chặn mặt sau khi quét từ camera
"""

import sys
from pathlib import Path

# Thêm thư mục gốc vào sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

FRONT_CCCD_PATH = ROOT_DIR / "data/input/cccd1.jpg"
BACK_CCCD_PATH = ROOT_DIR / "data/detect_card/id-card-side-object-detection.v1i.yolov8/valid/images/E0105823548_jpg.rf.26bcf2c5c457154afb2a3967d29ea178.jpg"
STUDENT_CARD_PATH = ROOT_DIR / "data/input/student_test.jpg"


def test_rule_1_front_cccd():
    print("\n[QUY TẮC 1] Kiểm tra camera-probe với Mặt Trước CCCD...")
    assert FRONT_CCCD_PATH.exists(), f"Không tìm thấy ảnh mẫu mặt trước: {FRONT_CCCD_PATH}"

    with open(FRONT_CCCD_PATH, "rb") as f:
        res = client.post("/predict/camera-probe", files={"file": ("front.jpg", f, "image/jpeg")})

    assert res.status_code == 200, f"Lỗi gọi API: {res.status_code}"
    data = res.json()
    print("   Phản hồi:", data)

    assert data.get("side") == "front", f"Mong muốn side='front', thực tế: {data.get('side')}"
    assert data.get("color") == "green", f"Mong muốn color='green', thực tế: {data.get('color')}"
    assert data.get("can_capture") is True or data.get("detected") is True, "Mặt trước CCCD phải cho phép chụp"
    print("   ✅ [PASS] Mặt trước CCCD: Báo xanh, cho phép chụp thành công.")


def test_rule_2_back_cccd():
    print("\n[QUY TẮC 2] Kiểm tra camera-probe với Mặt Sau CCCD...")
    assert BACK_CCCD_PATH.exists(), f"Không tìm thấy ảnh mẫu mặt sau: {BACK_CCCD_PATH}"

    with open(BACK_CCCD_PATH, "rb") as f:
        res = client.post("/predict/camera-probe", files={"file": ("back.jpg", f, "image/jpeg")})

    assert res.status_code == 200, f"Lỗi gọi API: {res.status_code}"
    data = res.json()
    print("   Phản hồi:", data)

    assert data.get("side") == "back", f"Mong muốn side='back', thực tế: {data.get('side')}"
    # Thông báo phải nêu rõ là mặt sau của CCCD
    msg = data.get("message", "").lower()
    assert "mặt sau của cccd" in msg or "mặt sau cccd" in msg, f"Thông báo phải nêu rõ 'mặt sau của CCCD', thực tế: {msg}"
    # Không cho phép chụp tự động trích xuất mặt sau
    assert data.get("can_capture") is False or data.get("detected") is False, "Mặt sau không được kích hoạt auto-capture trích xuất"
    print("   ✅ [PASS] Mặt sau CCCD: Hiển thị đúng thông báo 'Đây là mặt sau của CCCD'.")


def test_rule_3_other_card_rejection():
    print("\n[QUY TẮC 3] Kiểm tra camera-probe với Thẻ Khác (Thẻ Sinh Viên / Thẻ Khác)...")
    assert STUDENT_CARD_PATH.exists(), f"Không tìm thấy ảnh mẫu thẻ sinh viên: {STUDENT_CARD_PATH}"

    with open(STUDENT_CARD_PATH, "rb") as f:
        res = client.post("/predict/camera-probe", files={"file": ("student.jpg", f, "image/jpeg")})

    assert res.status_code == 200, f"Lỗi gọi API: {res.status_code}"
    data = res.json()
    print("   Phản hồi:", data)

    assert data.get("color") == "red", f"Thẻ khác bắt buộc BÁO ĐỎ (color='red'), thực tế: {data.get('color')}"
    assert data.get("side") == "invalid_card", f"Mong muốn side='invalid_card', thực tế: {data.get('side')}"
    assert data.get("can_capture") is False or data.get("detected") is False, "Thẻ khác tuyệt đối không được phép chụp (can_capture=False)"
    print("   ✅ [PASS] Thẻ khác: Báo đỏ rực, khóa chức năng chụp.")


def test_rule_4_pipeline_security():
    print("\n[QUY TẮC 4] Kiểm tra Chốt chặn bảo vệ API /predict/image khi người dùng gửi ảnh từ Camera...")
    
    # 4.1 Thẻ khác -> Phải bị từ chối
    with open(STUDENT_CARD_PATH, "rb") as f:
        res_other = client.post("/predict/image", files={"file": ("student.jpg", f, "image/jpeg")}, data={"input_source": "WEBCAM"})
    assert res_other.status_code in (400, 422), f"Thẻ khác phải bị từ chối 400/422, thực tế: {res_other.status_code}"
    print("   ✅ [PASS] /predict/image từ chối thẻ sinh viên / thẻ khác.")

    # 4.2 Mặt sau CCCD -> Phải báo rõ đây là mặt sau
    with open(BACK_CCCD_PATH, "rb") as f:
        res_back = client.post("/predict/image", files={"file": ("back.jpg", f, "image/jpeg")}, data={"input_source": "WEBCAM"})
    assert res_back.status_code == 400, f"Mặt sau CCCD phải trả về 400, thực tế: {res_back.status_code}"
    err_msg = res_back.json().get("error", "")
    assert "mặt sau" in err_msg.lower(), f"Lỗi phải nêu rõ mặt sau, thực tế: {err_msg}"
    print("   ✅ [PASS] /predict/image từ chối mặt sau với thông báo chuẩn.")


if __name__ == "__main__":
    print("=" * 65)
    print("🎯 CHẠY KIỂM THỬ QUY TẮC CAMERA AI (CAMERA RULES VERIFICATION)")
    print("=" * 65)
    test_rule_1_front_cccd()
    test_rule_2_back_cccd()
    test_rule_3_other_card_rejection()
    test_rule_4_pipeline_security()
    print("\n" + "=" * 65)
    print("🎉 TOÀN BỘ 4 QUY TẮC CAMERA ĐỀU VƯỢT QUA KIỂM THỬ (100% PASS)!")
    print("=" * 65 + "\n")
