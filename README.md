# 🪪 OCR_CCCD — Vietnamese ID Card OCR Pipeline

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF?style=for-the-badge)
![EasyOCR](https://img.shields.io/badge/EasyOCR-1.7.2-FF6B35?style=for-the-badge)
![OpenCV](https://img.shields.io/badge/OpenCV-4.13-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Hệ thống nhận dạng và trích xuất thông tin thẻ Căn cước công dân (CCCD) Việt Nam**  
sử dụng pipeline 2-Stage Object Detection với YOLOv8 + EasyOCR

[🚀 Bắt đầu nhanh](#-cài-đặt) • [📖 Tài liệu](#-cách-hoạt-động) • [🗂️ Cấu trúc](#️-cấu-trúc-thư-mục)

</div>

---

## ✨ Tính năng nổi bật

| Tính năng | Mô tả |
|---|---|
| 🔍 **2-Stage Detection** | Stage 1 phát hiện & cắt thẻ, Stage 2 định vị 8 trường thông tin |
| 🤖 **Dual OCR Engine** | EasyOCR (chính) + Tesseract (dự phòng) cho độ chính xác cao |
| 🖼️ **GUI Application** | Giao diện đồ họa thân thiện để dùng trực tiếp |
| 🛡️ **Phát hiện mặt sau** | Tự động từ chối ảnh mặt sau CCCD |
| 📊 **Visualization** | Vẽ bounding box màu sắc cho từng trường |
| 📦 **Batch Processing** | Xử lý hàng loạt ảnh với `test_batch.py` |
| ✅ **Validation** | Kiểm tra format số CCCD, ngày sinh, ngày hết hạn |

---

## 🛠️ Yêu cầu hệ thống

- **OS**: macOS hoặc Linux
- **Python**: 3.11+ (đã test trên 3.13)
- **RAM**: Tối thiểu 4GB (khuyến nghị 8GB+)
- **Tesseract**: Cài đặt qua Homebrew (macOS) hoặc apt (Linux)

---

## 🚀 Cài đặt

### Bước 1 — Clone repository

```bash
git clone https://github.com/HoangKhai1612/OCR_CCCD.git
cd OCR_CCCD
```

### Bước 2 — Tạo môi trường ảo Python

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### Bước 3 — Cài đặt dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Bước 4 — Cài đặt Tesseract

**macOS (Homebrew):**
```bash
brew install tesseract tesseract-lang
```

**Ubuntu / Debian:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-vie
```

### Bước 5 — Tải model weights

Đặt các file model vào thư mục `models/`:
```
models/
├── yolov8_cccd_detect.pt   ← Model Stage 1: Phát hiện thẻ CCCD
└── yolov8_fields.pt        ← Model Stage 2: Phát hiện 8 trường
```

---

## 🎯 Cách sử dụng

### Chạy pipeline chính

```bash
# Cách 1: Dùng script helper (khuyến nghị)
./run.sh

# Cách 2: Chạy trực tiếp với SSL fix cho EasyOCR
SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())") python3 main.py

# Cách 3: Chạy trực tiếp
python3 main.py
```

### Chạy giao diện đồ họa (GUI)

```bash
python3 gui_app.py
```

### Xử lý batch nhiều ảnh

```bash
python3 test_batch.py
```

---

## 🔬 Cách hoạt động

Pipeline xử lý qua **5 bước** tuần tự:

```
[Ảnh đầu vào]
      │
      ▼
┌─────────────────────────────────┐
│  Stage 1: Card Detection        │  YOLOv8 phát hiện & cắt thẻ CCCD
│  (yolov8_cccd_detect.pt)        │  Từ chối nếu là mặt sau
└──────────────┬──────────────────┘
               │ card_cropped.jpg
               ▼
┌─────────────────────────────────┐
│  Stage 2: Field Detection       │  YOLOv8 định vị 8 trường thông tin
│  (yolov8_fields.pt)             │  → số CCCD, họ tên, ngày sinh...
└──────────────┬──────────────────┘
               │ 8 vùng crop
               ▼
┌─────────────────────────────────┐
│  Enhancement                    │  Tăng cường ảnh, khử nhiễu
│  (enhancer.py)                  │  Chỉnh độ tương phản
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│  OCR Engine                     │  EasyOCR (chính)
│  (ocr_engine.py)                │  Tesseract (dự phòng)
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│  Validation & Export            │  Kiểm tra format, xuất JSON/TXT
│  (validator.py)                 │
└─────────────────────────────────┘
```

### 8 trường thông tin được trích xuất

| Field | Tên tiếng Việt | Màu Bounding Box |
|---|---|---|
| `id` | Số CCCD | 🔴 Đỏ |
| `name` | Họ và tên | 🟢 Xanh lá |
| `dob` | Ngày sinh | 🔵 Xanh dương |
| `gender` | Giới tính | 🟡 Vàng |
| `nationality` | Quốc tịch | 🟣 Hồng |
| `origin_place` | Quê quán | 🩵 Cyan |
| `current_place` | Nơi cư trú | 🟠 Cam |
| `expire_date` | Ngày hết hạn | ⚫ Đen |

---

## 🗂️ Cấu trúc thư mục

```
OCR_CCCD/
├── 📁 src/                     # Module nguồn
│   ├── detector_yolo.py        # Stage 1 & 2 YOLO detection
│   ├── enhancer.py             # Tiền xử lý & tăng cường ảnh
│   ├── extractor.py            # Trích xuất thông tin
│   ├── extractor_yolo.py       # Trích xuất dùng YOLO
│   ├── ocr_engine.py           # EasyOCR + Tesseract engine
│   ├── pipeline_v2.py          # Pipeline tổng hợp v2
│   ├── quality_check.py        # Kiểm tra chất lượng ảnh
│   └── validator.py            # Validation kết quả OCR
│
├── 📁 models/                  # YOLO model weights (không commit)
├── 📁 config/                  # Cấu hình regex, settings
├── 📁 input/                   # Ảnh đầu vào
├── 📁 output/                  # Kết quả xử lý
│   ├── card_cropped.jpg        # Thẻ đã cắt sạch nền
│   ├── cccd_fields_visualization.jpg  # Ảnh tổng hợp 8 khung
│   └── detected_fields/        # 8 ảnh crop từng trường
├── 📁 results/                 # Kết quả OCR
│   ├── json/                   # Kết quả dạng JSON
│   └── txt/                    # Kết quả dạng văn bản
├── 📁 scripts/                 # Script tiện ích
│
├── main.py                     # Entry point chính
├── gui_app.py                  # Giao diện đồ họa
├── test_batch.py               # Xử lý batch
├── download_data.py            # Tải dữ liệu training
├── run.sh                      # Script chạy nhanh
└── requirements.txt            # Python dependencies
```

---

## ⚙️ Cấu hình

Chỉnh sửa `config/settings.py` để tuỳ chỉnh:

```python
# Đường dẫn Tesseract (nếu không tự phát hiện)
TESSERACT_CMD = "/usr/local/bin/tesseract"

# Ngưỡng confidence cho YOLO
STAGE1_CONF = 0.6
STAGE2_CONF = 0.5
```

---

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng:

1. Fork repository
2. Tạo branch mới: `git checkout -b feature/ten-tinh-nang`
3. Commit thay đổi: `git commit -m 'feat: Thêm tính năng X'`
4. Push branch: `git push origin feature/ten-tinh-nang`
5. Tạo Pull Request

---

## 📄 License

Dự án này được phân phối dưới giấy phép **MIT**. Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

---

## ⚠️ Lưu ý

> **Bảo mật dữ liệu**: Đây là dự án nghiên cứu & học thuật. Không sử dụng để xử lý thông tin CCCD thật của người khác mà không có sự đồng ý. Tuân thủ quy định pháp luật về bảo vệ dữ liệu cá nhân (Nghị định 13/2023/NĐ-CP).

---

<div align="center">
Made with ❤️ in Vietnam 🇻🇳
</div>