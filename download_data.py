# download_data.py
# Tải dataset từ Roboflow. API key đọc từ biến môi trường ROBOFLOW_API_KEY
# (đặt trong file .env ở thư mục gốc repo — xem .env.example).
import os

# pyrefly: ignore [missing-import]
from roboflow import Roboflow

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

api_key = os.environ.get("ROBOFLOW_API_KEY")
if not api_key:
    raise SystemExit("Thiếu ROBOFLOW_API_KEY — thêm dòng ROBOFLOW_API_KEY=... vào file .env")
rf = Roboflow(api_key=api_key)
# Kéo từ workspace của lams-workspace
project = rf.workspace("lams-workspace").project("id-card-side-object-detection")
version = project.version(1)

print("Đang tải dataset mặt trước/mặt sau...")
dataset = version.download("yolov8")
print("Tải xong! Dataset nằm tại:", dataset.location)
