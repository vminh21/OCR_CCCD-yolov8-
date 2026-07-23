# download_data.py
from roboflow import Roboflow

rf = Roboflow(api_key="yVkspAfx8GI5gcRPvIhk")
# Kéo từ workspace của lams-workspace
project = rf.workspace("lams-workspace").project("id-card-side-object-detection")
version = project.version(1)

print("Đang tải dataset mặt trước/mặt sau...")
dataset = version.download("yolov8")
print("Tải xong! Dataset nằm tại:", dataset.location)