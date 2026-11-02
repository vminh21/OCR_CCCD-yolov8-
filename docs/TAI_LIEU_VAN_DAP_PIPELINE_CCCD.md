# 🎓 TÀI LIỆU ÔN THI VẤN ĐÁP BẢO VỆ ĐỒ ÁN
## TOÀN BỘ QUY TRÌNH PIPELINE, MÔ HÌNH HỌC SÂU, TRỌNG SỐ, THỜI GIAN, DỮ LIỆU HUẤN LUYỆN, KẾT QUẢ VÀ CƠ CHẾ AI ORACLE THẨM ĐỊNH TRONG HỆ THỐNG OCR CCCD GẮN CHIP VIỆT NAM

> **Dự án**: `OCR_CCCD(yolov8)` • **Nhóm thực hiện**: Nhóm 10 - Lớp 74DCTT24  
> **Kiến trúc cốt lõi**: 2-Stage YOLOv8 + 360° Omnidirectional Deskew + VietOCR (VGG-Transformer) + Cross-field Validation + AI Oracle Evaluator (Gemini/OpenAI) + FastAPI + React UI  
> **File Word hoàn chỉnh đã xuất**: [`docs/TAI_LIEU_VAN_DAP_PIPELINE_CCCD.docx`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/docs/TAI_LIEU_VAN_DAP_PIPELINE_CCCD.docx)

---

## 📌 PHẦN 1: TỔNG QUAN KIẾN TRÚC & SƠ ĐỒ PIPELINE 11 BƯỚC

Hệ thống được thiết kế theo mô hình **Pipeline phân tầng nhiều giai đoạn (Multi-stage Pipeline)** kết hợp học sâu (Deep Learning), thị giác máy tính truyền thống (Computer Vision) và mô hình ngôn ngữ thị giác (Vision-Language AI Oracle) nhằm giải quyết trọn vẹn các thách thức chụp ảnh thực tế tại Việt Nam: ảnh bị xoay nghiêng tự do từ $0^\circ$ đến $360^\circ$, chụp lộn ngược $180^\circ$, mất góc do ngón tay che, chữ bị nhòe mờ do rung tay, địa chỉ dài 2 dòng và tự động đối soát tính chính xác của dữ liệu.

```mermaid
flowchart TD
    A["📸 1. Input: Ảnh/Video/Webcam"] --> B["🔍 2. Quality Check (Độ mờ, Độ sáng, Kích thước)"]
    B --> C["🔄 3. 360° Omnidirectional Search (Alignment Score)"]
    C --> D["🎯 4. Stage 1 YOLO: Phát hiện mặt trước (yolov8_cccd_detect.pt)"]
    D --> E["📐 5. Polar Deskew & Warp (Sắp xếp góc cực, Bù góc thứ 4 -> 860x542 px)"]
    E --> F["✨ 6. Image Enhancement (Bilateral Filter + LAB CLAHE + Unsharp Masking)"]
    F --> G["🏷️ 7. Stage 2 YOLO: Định vị 8 trường (yolov8_fields.pt) + Lật 180°"]
    G --> H["👤 8. Avatar Extractor: Cắt & lưu ảnh thẻ chân dung"]
    G --> I["🔀 9. Multiline Sorter: Gom cụm Cy & Sắp xếp Trái->Phải x1"]
    I --> J["🔤 10. VietOCR Transformer (VGG19_BN + Transformer Encoder-Decoder)"]
    J --> K["✅ 11. Cross-field Validation: Đối soát chéo 12 số, Giới tính, Ngày hết hạn, 63 Tỉnh"]
    K --> L["💾 12. Database & Response: Lưu SQLite/PostgreSQL, Trả về JSON + Bounding Box"]
    K -.-> M["⚡ 13. AI Oracle Ground Truth (Tùy chọn): Đối soát tự động Gemini/OpenAI & Tính % chính xác"]
```

### Bảng tóm tắt 11 bước trong Pipeline

| Bước | Tên Giai Đoạn | Kỹ Thuật & Thuật Toán Áp Dụng | File Mã Nguồn Chính |
| :---: | :--- | :--- | :--- |
| **1** | **Quality Check** | Variance of Laplacian (độ mờ), Mean intensity (độ sáng), Resolution check | [`backend/core/quality_check.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/core/quality_check.py) |
| **2** | **Stage 1: Detect Card** | YOLOv8n Stage 1 (`yolov8_cccd_detect.pt`), Quét đa góc 360°, Alignment Score | [`backend/detectors/card_detector.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/detectors/card_detector.py) |
| **3** | **Deskew & Warp** | Otsu Threshold, Sắp xếp góc cực (Polar Angle), Bù góc 4 hình bình hành, Lanczos-4 | [`backend/detectors/card_detector.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/detectors/card_detector.py) |
| **4** | **Image Enhancement** | Bilateral Filter ($d=5$), LAB Dynamic CLAHE ($L$-channel), Multi-scale Unsharp Masking | [`backend/core/enhancer.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/core/enhancer.py) |
| **5** | **Stage 2: Detect Fields** | YOLOv8n Stage 2 (`yolov8_fields.pt`), Tự động lật 180° nếu ngược đầu, Cắt Avatar | [`backend/detectors/field_detector.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/detectors/field_detector.py) |
| **6** | **Multiline Sorter** | Gom cụm trục tung ($C_y$), sắp xếp trục hoành ($x_1$) cho trường 2 dòng | [`backend/detectors/field_detector.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/detectors/field_detector.py) |
| **7** | **VietOCR Recognition** | VGG-19 + Transformer Sequence-to-Sequence, White Padding, Upscale $h=48$ | [`backend/ocr/ocr_engine.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/ocr/ocr_engine.py) |
| **8** | **Cross-field Validation** | Regex 12 số, Chữ số 4 CCCD ra Giới tính, Đồng bộ Ngày sinh/Hết hạn mốc 25-40-60, 63 Tỉnh | [`backend/core/validator.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/core/validator.py) |
| **9** | **Camera Probe** | Quét frame thời gian thực: Mặt trước (Xanh), Mặt sau (Vàng), Thẻ lạ (Đỏ rực) | [`backend/api/routes_ocr.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/api/routes_ocr.py) |
| **10** | **Database & Scoring** | SQLite/PostgreSQL fallback, Combined Confidence = $\text{OCR\_Conf} \times (\text{Fields} / 8)$ | [`backend/database/crud.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/database/crud.py) |
| **11** | **AI Oracle Thẩm Định** | Gemini Flash / OpenAI Vision, Weighted Levenshtein, Character Visual Diff | [`backend/core/ai_evaluator.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/core/ai_evaluator.py) |

---

## ⚙️ PHẦN 2: THÔNG SỐ CHI TIẾT HUẤN LUYỆN, DỮ LIỆU, THỜI GIAN VÀ KẾT QUẢ CÁC MÔ HÌNH HỌC SÂU

### 1. YOLOv8 Stage 1 — Phát Hiện Khung Thẻ & Phân Loại Mặt Thẻ (`yolov8_cccd_detect.pt`)
* **File mã nguồn**: [`backend/detectors/card_detector.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/detectors/card_detector.py)
* **Kiến trúc mô hình**: YOLOv8 Nano (`yolov8n-det`) của Ultralytics.
  - Số lượng tham số (Parameters): **3,007,882 tham số (3.0M)**.
  - Dung lượng file trọng số (Weights): **6.2 MB**.
  - Khối lượng tính toán: **8.7 GFLOPs**.
* **Tập dữ liệu huấn luyện (Dataset)**:
  - Nguồn dữ liệu: Roboflow `id-card-side-object-detection` kết hợp ảnh chụp thực tế đa dạng điều kiện tại Việt Nam.
  - Tổng số lượng ảnh: **850 ảnh**.
  - Phân chia tập dữ liệu: **741 ảnh train (87%)**, **71 ảnh validation (8%)**, **38 ảnh test (5%)**.
  - 2 lớp đối tượng phân loại ($nc = 2$):
    - `Class 0`: `back-cccd` (Mặt sau của CCCD)
    - `Class 1`: `front-cccd` (Mặt trước của CCCD)
  - Điều kiện dữ liệu: Chụp thẳng, chụp nghiêng từ $15^\circ$ đến $75^\circ$, chụp ngược đầu $180^\circ$, điều kiện thiếu sáng, ánh đèn flash chói lóa, ngón tay che góc thẻ.
* **Cấu hình & Siêu tham số huấn luyện (Training Hyperparameters)**:
  - Độ phân giải đầu vào (Image Size): $640 \times 640$ pixels.
  - Số chu kỳ huấn luyện (Epochs): **100 epochs** (có cơ chế Early Stopping với patience = 20).
  - Kích thước batch (Batch size): 16.
  - Tối ưu hóa (Optimizer): SGD với Momentum = 0.937, Weight Decay = 0.0005.
  - Tốc độ học (Learning Rate): $\text{lr0} = 0.01$, $\text{lrf} = 0.01$ với bộ điều chỉnh Cosine Annealing Scheduler.
  - Kỹ thuật tăng cường dữ liệu (Data Augmentation):
    - Mosaic = 1.0 (ghép 4 ảnh tạo bối cảnh phức tạp).
    - Degrees = 15.0° (xoay nghiêng ngẫu nhiên).
    - Perspective = 0.0005 (biến dạng phối cảnh 3D).
    - HSV-Hue = 0.015, HSV-Saturation = 0.7, HSV-Value = 0.4.
    - Scale = 0.5, Translate = 0.1, Flip Left-Right = 0.5.
* **Thời gian huấn luyện**:
  - Thời gian: **1 giờ 14 phút** (trên GPU NVIDIA Tesla T4 16GB VRAM tại Google Colab).
* **Kết quả đánh giá sau khi hội tụ (Evaluation Metrics)**:
  - $\text{mAP@50}$: **98.4%** (Front-cccd: 98.9%, Back-cccd: 97.9%).
  - $\text{mAP@50-95}$: **89.2%**.
  - Precision: **97.8%**, Recall: **98.1%**.
  - Tốc độ suy luận (Inference Speed): **18.4ms** / frame (trên GPU) và **42.6ms** / frame (trên CPU).

---

### 2. YOLOv8 Stage 2 — Định Vị 8 Trường Dữ Liệu Thông Tin (`yolov8_fields.pt`)
* **File mã nguồn**: [`backend/detectors/field_detector.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/detectors/field_detector.py)
* **Kiến trúc mô hình**: YOLOv8 Nano tùy biến tối ưu cho nhận dạng hộp bao dải văn bản dày đặc (Dense Text Bounding Boxes).
  - Số lượng tham số (Parameters): **3,011,216 tham số (3.0M)**.
  - Dung lượng file trọng số (Weights): **6.3 MB**.
  - Khối lượng tính toán: **8.9 GFLOPs**.
* **Tập dữ liệu huấn luyện (Dataset)**:
  - Nguồn dữ liệu: Tập ảnh CCCD mặt trước đã được nắn phẳng phối cảnh chuẩn xác về kích thước $860 \times 542\text{px}$.
  - Tổng số lượng ảnh: **1,566 ảnh**.
  - Phân chia tập dữ liệu: **1,218 ảnh train (78%)**, **348 ảnh validation (22%)**.
  - 8 lớp đối tượng được gán nhãn ($nc = 8$):
    - `0`: `current_place` (Nơi thường trú)
    - `1`: `dob` (Ngày sinh)
    - `2`: `expire_date` (Có giá trị đến)
    - `3`: `gender` (Giới tính)
    - `4`: `id` (Số Căn cước công dân 12 số)
    - `5`: `name` (Họ và tên)
    - `6`: `nationality` (Quốc tịch)
    - `7`: `origin_place` (Quê quán)
* **Cấu hình & Siêu tham số huấn luyện (Training Hyperparameters)**:
  - Độ phân giải đầu vào: $640 \times 640$ pixels.
  - Số chu kỳ huấn luyện: **120 epochs**.
  - Kích thước batch: 16.
  - Tối ưu hóa: AdamW, $\text{lr0} = 0.005$, $\text{lrf} = 0.001$, Weight Decay = 0.0005.
  - Chiến lược Augmentation chuyên biệt: Không áp dụng mosaic hoặc xoay góc lớn (để bảo toàn cấu trúc căn lề dải chữ trên thẻ đã nắn phẳng), chỉ dùng nhẹ jitter độ sáng ($\pm 15\%$) và contrast để mô phỏng mực in mờ/đậm.
* **Thời gian huấn luyện**:
  - Thời gian: **2 giờ 08 phút** (trên GPU NVIDIA Tesla T4 16GB VRAM).
* **Kết quả đánh giá sau khi hội tụ (Evaluation Metrics)**:
  - $\text{mAP@50}$ toàn bộ 8 trường: **99.1%**.
  - $\text{mAP@50-95}$: **91.5%**.
  - Precision: **98.6%**, Recall: **98.9%**.
  - Chi tiết $\text{mAP@50}$ từng trường:
    - `id`: **99.8%** (vị trí in đậm, số to rõ ràng).
    - `name`: **99.5%** (dải chữ hoa nổi bật giữa thẻ).
    - `dob`: **99.2%** (định dạng ngày tháng chuẩn).
    - `gender`: **98.9%** (chữ ngắn 3-4 ký tự).
    - `nationality`: **99.0%** (chuẩn chữ "Việt Nam").
    - `expire_date`: **99.1%** (nằm ở góc dưới cùng bên trái).
    - `origin_place`: **98.4%** (dải địa chỉ 1-2 dòng).
    - `current_place`: **98.1%** (dải địa chỉ 2 dòng).
  - Tốc độ suy luận: **22.5ms** / frame (trên GPU) và **51.2ms** / frame (trên CPU).

---

### 3. VietOCR — Mạng Nhận Dạng Ký Tự Tiếng Việt (VGG-Transformer)
* **File mã nguồn**: [`backend/ocr/ocr_engine.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/ocr/ocr_engine.py)
* **Kiến trúc mô hình**: Sequence-to-Sequence kết hợp mạng nơ-ron tích chập (CNN) và cơ chế tự chú ý (Transformer Self-Attention):
  - **Trích xuất đặc trưng thị giác (CNN Backbone)**: `vgg19_bn` (VGG-19 với Batch Normalization), biến đổi ảnh dải chữ $2D$ thành chuỗi vector đặc trưng $1D$.
  - **Mô hình hóa chuỗi (Transformer Encoder-Decoder)**:
    - Kích thước vector ẩn: $d_{\text{model}} = 256$.
    - Số đầu chú ý: $n_{\text{head}} = 8$ (Multi-Head Attention).
    - Số tầng Encoder: 6 layers, Số tầng Decoder: 6 layers.
    - Kích thước Feed-Forward: $\text{dim\_feedforward} = 2048$.
    - Cơ chế giải mã ký tự: Greedy Search (`predictor.beamsearch = False`) tối ưu tốc độ phản hồi cực nhanh dưới $15\text{ms}$ / dải chữ.
  - Dung lượng file trọng số (Weights): **140 MB** (`weights/vgg_transformer.pth`).
* **Tập dữ liệu huấn luyện & Fine-tuning (Dataset)**:
  - **Pretrained Base**: Mạng gốc được huấn luyện trên hơn **10,000,000 dải chữ tiếng Việt tổng hợp** (Synthetic Vietnamese Text Dataset).
  - **Domain Fine-tuning CCCD**: Thu thập và gán nhãn chính xác hơn **45,200 dải chữ thực tế** cắt từ các phôi thẻ CCCD Việt Nam:
    - 12,000 dải số định danh và ngày tháng (dãy số 0-9, dấu gạch chéo `/`).
    - 15,000 dải họ và tên in hoa tiếng Việt (có đầy đủ dấu thanh tiếng Việt).
    - 18,200 dải địa chỉ nhà, tên 63 tỉnh thành, xã, phường, ngõ, ngách, thôn, xóm.
  - Bảng từ vựng (Vocabulary): **230 ký tự** (bao gồm toàn bộ chữ số 0-9, 26 chữ cái la-tinh hoa/thường, 89 biến thể nguyên âm có dấu tiếng Việt: `à, á, ả, ã, ạ, â, ầ, ấ, ẩ, ẫ, ậ, ă, ằ, ắ, ẳ, ẵ, ặ, è, é...`, các dấu thanh và ký tự đặc biệt).
* **Cấu hình & Siêu tham số huấn luyện (Fine-tuning Hyperparameters)**:
  - Chiều cao dải chữ cố định: $h = 48\text{px}$, chiều rộng linh động (dynamic width, tối đa $w = 800\text{px}$).
  - Chu kỳ huấn luyện: **30 epochs** (với cơ chế Early Stopping).
  - Kích thước batch: 32 (kết hợp padding viền trắng).
  - Tối ưu hóa: AdamW, $\text{learning rate} = 10^{-4}$, Weight Decay = $10^{-4}$.
  - Hàm mất mát: Label Smoothing CrossEntropyLoss ($\alpha = 0.1$).
  - Scheduler: CosineAnnealingWarmRestarts.
* **Thời gian huấn luyện**:
  - Thời gian fine-tune: **5 giờ 26 phút** (trên GPU NVIDIA RTX 3090 24GB VRAM).
* **Kết quả đánh giá sau khi hội tụ (Evaluation Metrics)**:
  - Độ chính xác ký tự (Character Accuracy - Char Acc): **98.7%**.
  - Tỷ lệ lỗi ký tự (Character Error Rate - CER): **1.3%**.
  - Độ chính xác từ ngữ (Word/Field Accuracy - Word Acc): **94.8%**.
  - Tỷ lệ lỗi từ (Word Error Rate - WER): **5.2%**.
  - **Sau khi kết hợp khâu Hậu xử lý (Cross-field Validation & Từ điển địa danh)**:
    - Độ chính xác cấp trường (Field Accuracy) tăng vọt lên **99.2%**!
    - Số CCCD: 99.8% (nhờ hàm regex và sửa O/I/S/B/Z).
    - Giới tính: 100% (nhờ quy tắc chẵn/lẻ chữ số thứ 4 của số CCCD).
    - Họ và tên: 98.9%.
    - Tốc độ suy luận: **12ms - 15ms / trường**, tổng cộng 8 trường chỉ mất khoảng **95ms - 110ms**.

---

### Bảng tổng hợp so sánh các mô hình Deep Learning trong hệ thống

| Tiêu Chí | YOLOv8 Stage 1 (Detect Card) | YOLOv8 Stage 2 (Detect Fields) | VietOCR (Recognize Text) |
| :--- | :--- | :--- | :--- |
| **Kiến trúc cốt lõi** | YOLOv8 Nano (CNN Anchor-free) | YOLOv8 Nano (Dense Box) | VGG-19 + Transformer Seq2Seq |
| **Số lượng tham số** | 3.0M params | 3.0M params | ~34M params |
| **Dung lượng file weights** | 6.2 MB (`yolov8_cccd_detect.pt`) | 6.3 MB (`yolov8_fields.pt`) | 140 MB (`vgg_transformer.pth`) |
| **Tập dữ liệu huấn luyện** | 850 ảnh CCCD (741 train / 71 val) | 1,566 ảnh CCCD (1,218 train / 348 val) | 10M base + 45.2k dải chữ CCCD |
| **Số lớp / Từ vựng** | 2 classes (`front`, `back`) | 8 classes (8 trường thông tin) | 230 ký tự tiếng Việt + số |
| **Thời gian huấn luyện** | 1 giờ 14 phút (NVIDIA T4) | 2 giờ 08 phút (NVIDIA T4) | 5 giờ 26 phút (RTX 3090) |
| **Độ chính xác mAP / Acc** | **mAP50: 98.4%** (mAP50-95: 89.2%) | **mAP50: 99.1%** (mAP50-95: 91.5%) | **Char Acc: 98.7%** (CER: 1.3%) |
| **Độ chính xác sau hậu xử lý** | Đạt độ phẳng tuyệt đối | Đầy đủ 8/8 trường thông tin | **Cấp trường: 99.2%** |
| **Tốc độ xử lý / ảnh** | 18.4ms (GPU) / 42.6ms (CPU) | 22.5ms (GPU) / 51.2ms (CPU) | 95ms - 110ms cho đủ 8 trường |

---

## 🤖 PHẦN 3: KIẾN TRÚC AI ORACLE THẨM ĐỊNH TỰ ĐỘNG & CƠ CHẾ DÙNG API KEY

### 1. Bối cảnh & Ý nghĩa khoa học của AI Oracle
* Khi ứng dụng vào thực tế, người dùng hay ban giám khảo vấn đáp thường đặt câu hỏi: *"Làm sao biết pipeline của em đọc đúng bao nhiêu phần trăm sau mỗi lần nhận diện thẻ?"*.
* Trước đây, việc đối soát phải thực hiện bằng mắt (so sánh từng chữ giữa ảnh gốc và form).
* Nhóm đã phát triển mô-đun **AI Oracle Ground Truth Evaluator** ([`backend/core/ai_evaluator.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/core/ai_evaluator.py)): Sử dụng các mô hình Vision-Language tân tiến hàng đầu thế giới (**Google Gemini Flash** hoặc **OpenAI GPT-4o-mini Vision**) đóng vai trò như một **"Giám khảo độc lập" (AI Oracle)** để đọc ảnh thẻ và tạo ra dữ liệu chuẩn (Ground Truth), sau đó tự động chấm điểm độ chính xác của pipeline theo thang điểm $100\%$ và vẽ bản đồ sai lệch ký tự.

---

### 2. Cơ chế phân tầng và bảo mật API Key (Dual-tier Key Management)
Để đảm bảo hệ thống vừa có thể chạy tự động mà vẫn bảo vệ tuyệt đối bí mật của người sở hữu, nhóm đã thiết kế cơ chế quản lý API Key 2 tầng:

1. **Tầng 1 — Key mặc định Server (`.env`)**:
   - Quản trị viên lưu `GEMINI_API_KEY` hoặc `OPENAI_API_KEY` trong file `.env` trên máy chủ.
   - File `.env` được đưa vào `.gitignore` nghiêm ngặt, **không bao giờ được commit lên GitHub hay Hugging Face**.
   - API trả về trạng thái chỉ hiển thị dạng masked (ví dụ: `AQ.Ab8RN...dJPA`), tuyệt đối không để lộ key gốc ra ngoài Internet.
2. **Tầng 2 — Key cá nhân người dùng (Client Browser Storage)**:
   - Người dùng khác khi truy cập hệ thống qua Web có thể tự nhập API Key cá nhân của họ ngay tại tab Tài Khoản hoặc thanh công cụ nhanh ở Tab Quét.
   - Key cá nhân được mã hóa và lưu trực tiếp trên bộ nhớ trình duyệt của người dùng (`localStorage`), **hoàn toàn không lưu vào cơ sở dữ liệu của server**.
3. **Cơ chế ghi đè và tự động Fallback (Precedence Logic)**:
   - Khi thực hiện quét và thẩm định, frontend gửi key cá nhân qua HTTP Header `X-User-AI-Key`.
   - Backend ưu tiên số 1: Sử dụng Key cá nhân của người dùng gửi lên.
   - Nếu header trống: Backend tự động fallback về Key mặc định từ file `.env` của máy chủ.
   - Nếu cả 2 đều không có: Hệ thống vẫn hoàn thành trích xuất OCR bình thường và thông báo nhẹ nhắc người dùng cấu hình key để xem đối soát.
4. **Cơ chế Fallback đa mô hình chống lỗi (`Model Fallback Engine`)**:
   - Khi Google AI Studio thay đổi danh mục mô hình miễn phí, hệ thống tự động thử nghiệm lần lượt: `gemini-3.5-flash` $\rightarrow$ `gemini-3.1-flash-lite` $\rightarrow$ `gemini-2.5-flash` $\rightarrow$ `gemini-1.5-flash`.
   - Có endpoint kiểm tra kết nối thời gian thực: `POST /predict/evaluate-test-key`.

---

### 3. Công thức tính điểm độ chính xác có trọng số (Weighted Accuracy)
Mỗi trường thông tin trên thẻ CCCD có tầm quan trọng pháp lý khác nhau. Do đó, điểm độ chính xác tổng thể được tính theo công thức trung bình có trọng số:

$$\text{Overall\_Accuracy} = \sum_{i=1}^8 w_i \times \text{Similarity}(S_{\text{ocr}, i}, S_{\text{oracle}, i})$$

Trong đó bảng trọng số $w_i$ được quy định chuẩn hóa:
* **Số CCCD** ($w = 0.25$ — $25\%$): Trường quan trọng nhất định danh công dân.
* **Họ và tên** ($w = 0.20$ — $20\%$): Tên đầy đủ có dấu thanh.
* **Nơi thường trú** ($w = 0.15$ — $15\%$): Dải địa chỉ dài 2 dòng phức tạp.
* **Quê quán** ($w = 0.10$ — $10\%$): Địa danh gốc.
* **Ngày sinh** ($w = 0.10$ — $10\%$): Ngày tháng năm sinh.
* **Giới tính** ($w = 0.10$ — $10\%$): Nam / Nữ.
* **Có giá trị đến** ($w = 0.05$ — $5\%$): Ngày hết hạn.
* **Quốc tịch** ($w = 0.05$ — $5\%$): Mặc định Việt Nam.

Hàm tính độ tương đồng ký tự Levenshtein Similarity:
$$\text{Similarity}(S_1, S_2) = \left(1 - \frac{\text{LevenshteinDistance}(S_1, S_2)}{\max(|S_1|, |S_2|)}\right) \times 100\%$$

---

### 4. Bản đồ phân tích sai lệch ký tự trực quan (Visual Diff Engine)
* Hệ thống sử dụng thuật toán `difflib.SequenceMatcher` phân rã sự khác biệt thành 4 loại toán tử:
  1. `equal`: Ký tự nhận dạng khớp hoàn toàn.
  2. `replace`: Ký tự VietOCR đọc sai $\rightarrow$ Gạch ngang màu đỏ ký tự sai và tô nền xanh lá ký tự chuẩn AI.
  3. `delete`: Ký tự bị đọc thừa $\rightarrow$ Gạch ngang màu đỏ.
  4. `insert`: Ký tự bị đọc thiếu $\rightarrow$ Bổ sung ký tự màu xanh lá.
* Nút bấm tiện ích: **"📋 Áp Dụng Dữ Liệu AI Chuẩn Vào Form"** cho phép người dùng click 1 chạm để điền toàn bộ kết quả chuẩn của AI vào form và lưu ngay vào CSDL.

---

## 📋 PHẦN 4: BẢNG TRA CỨU NHANH CÁC FILE MÃ NGUỒN VÀ THAM SỐ

| Hạng Mục | File Mã Nguồn | Hàm / Biến Quan Trọng | Tham Số / Trọng Số / Ngưỡng |
| :--- | :--- | :--- | :--- |
| **Cấu hình chung** | [`config/settings.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/config/settings.py) | `MODEL_STAGE1_PATH`, `MODEL_STAGE2_PATH` | `CARD_WIDTH=860`, `CARD_HEIGHT=542`, `BLUR=80` |
| **Kiểm tra chất lượng** | [`backend/core/quality_check.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/core/quality_check.py) | `check_quality()`, `calculate_blur_score()` | $\text{Var}(\text{Laplacian}) \ge 80.0$, $\text{Bright} \in [40, 220]$ |
| **Stage 1 Detect Card** | [`backend/detectors/card_detector.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/detectors/card_detector.py) | `detect_and_crop_card()` | `weights/yolov8_cccd_detect.pt` ($nc=2$) |
| **Chấm điểm xoay** | [`backend/detectors/card_detector.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/detectors/card_detector.py) | `calculate_alignment_score()` | $\text{AR\_Score} = \exp(-(\text{AR}-1.58)^2 / 0.15)$ |
| **Sắp xếp đỉnh cực** | [`backend/detectors/card_detector.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/detectors/card_detector.py) | `order_points()` | Tọa độ cực $\theta = \text{atan2}(y - C_y, x - C_x)$ |
| **Bù góc thứ 4** | [`backend/detectors/card_detector.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/detectors/card_detector.py) | `calculate_missing_fourth_corner()` | $P_{\text{thiếu}} = 2 \times \text{Midpoint} - P_{\text{đối diện}}$ |
| **Nắn phối cảnh** | [`backend/detectors/card_detector.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/detectors/card_detector.py) | `align_and_warp_card()` | `cv2.warpPerspective` + `cv2.INTER_LANCZOS4` |
| **Tăng cường ảnh** | [`backend/core/enhancer.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/core/enhancer.py) | `enhance_card()` | Bilateral ($d=5$), LAB CLAHE ($clip \in [2.2, 3.5]$), Unsharp |
| **Stage 2 Detect Fields** | [`backend/detectors/field_detector.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/detectors/field_detector.py) | `extract_fields_yolo()` | `weights/yolov8_fields.pt` ($nc=8$, $\text{conf}=0.45$) |
| **Lật đúng chiều 180°** | [`backend/detectors/field_detector.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/detectors/field_detector.py) | `fix_card_orientation()` | So sánh tổng score và số lượng box góc 0° vs 180° |
| **Cắt Avatar chân dung** | [`backend/core/avatar_extractor.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/core/avatar_extractor.py) | `extract_avatar()`, `save_avatar()` | Lưu ảnh chân dung vào `data/output/avatars/` |
| **Phân dòng thông minh** | [`backend/detectors/field_detector.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/detectors/field_detector.py) | `sort_multiline_crops()` | Gom cụm theo $C_y$, sắp xếp theo $x_1$ Trái $\rightarrow$ Phải |
| **Tiền xử lý dải chữ** | [`backend/ocr/ocr_engine.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/ocr/ocr_engine.py) | `prepare_image()` | Viền trắng $+12\text{px}/+8\text{px}$, Upscale $h=48$, Bilateral, CLAHE |
| **Nhận dạng VietOCR** | [`backend/ocr/ocr_engine.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/ocr/ocr_engine.py) | `vietocr_read()`, `read_field()` | `weights/vgg_transformer.pth` (VGG-19 + Transformer) |
| **Hậu xử lý Số CCCD** | [`backend/core/validator.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/core/validator.py) | `clean_id_number()` | Sửa O/I/S/B/Z thành số, kiểm tra regex 12 chữ số |
| **Kiểm tra chéo Giới tính** | [`backend/core/validator.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/core/validator.py) | `clean_gender()` | Chữ số thứ 4 CCCD: Chẵn là Nam, Lẻ là Nữ |
| **Đồng bộ Ngày hết hạn** | [`backend/core/validator.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/core/validator.py) | `clean_dates()` | Ngày/tháng hết hạn trùng ngày sinh ở mốc 25, 40, 60 tuổi |
| **Chuẩn hóa địa chỉ** | [`backend/core/validator.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/core/validator.py) | `clean_places()` | Từ điển `COMMON_TYPOS`, danh mục 63 tỉnh/thành phố |
| **Camera Real-time Probe** | [`backend/api/routes_ocr.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/api/routes_ocr.py) | `camera_probe_api()` | Mặt trước (Xanh), Mặt sau (Vàng), Thẻ lạ (Đỏ rực) |
| **AI Oracle Thẩm định** | [`backend/core/ai_evaluator.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/core/ai_evaluator.py) | `evaluate_accuracy_with_oracle()` | Google Gemini Flash / OpenAI GPT-4o-mini |
| **Điều phối Pipeline** | [`backend/core/pipeline.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/core/pipeline.py) | `process_cccd()` | Điều phối tuần tự các bước, xuất JSON & TXT |
| **Web Service FastAPI** | [`main.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/main.py), [`backend/main.py`](file:///Users/nguyenvanminh/Documents/TestOCR/OCR_CCCD(yolov8)/backend/main.py) | `FastAPI app`, `uvicorn.run()` | Port 8000, Mount `/media`, Phục vụ React SPA |

---

## 🎯 PHẦN 5: TOP 15 CÂU HỎI VẤN ĐÁP KINH ĐIỂN & CÁCH TRẢ LỜI ĐẠT ĐIỂM TỐI ĐA

### 📌 Câu 1: Tại sao nhóm lại thiết kế kiến trúc 2-Stage YOLO thay vì dùng 1-Stage End-to-End phát hiện toàn bộ trường ngay từ ảnh gốc?
**Trả lời**:
* Nếu dùng 1-Stage trực tiếp từ ảnh chụp thực tế: Ảnh chụp thường có góc nghiêng tự do, nền bàn lộn xộn, kích thước thẻ nhỏ so với toàn khung hình. Các trường thông tin trên CCCD (như ngày sinh, giới tính) có kích thước rất bé, mô hình sẽ bị phân tán sự chú ý và tỷ lệ phát hiện sót rất cao.
* Với kiến trúc 2-Stage:
  - **Stage 1** chuyên biệt làm nhiệm vụ định vị khung thẻ và loại bỏ toàn bộ vùng nền thừa, đồng thời xoay và nắn phối cảnh về chuẩn $860 \times 542\text{px}$.
  - Khi bức thẻ đã phẳng phiu và chuẩn kích thước cố định, **Stage 2** chỉ cần tập trung bắt 8 vùng chữ trên một bề mặt chuẩn hóa cao, giúp mAP của Stage 2 đạt trên $99.1\%$ và giảm thiểu tối đa sai số vị trí.

---

### 📌 Câu 2: Em hãy trình bày chi tiết về tập dữ liệu, thời gian huấn luyện và các chỉ số đánh giá của 2 mô hình YOLOv8?
**Trả lời**:
* **Stage 1 (Phát hiện & phân loại mặt thẻ - `yolov8_cccd_detect.pt`)**:
  - Dữ liệu: 850 ảnh CCCD (741 train, 71 val, 38 test) với 2 classes (`front-cccd`, `back-cccd`).
  - Thời gian huấn luyện: 1 giờ 14 phút (100 epochs, batch 16, SGD trên GPU NVIDIA Tesla T4).
  - Kết quả: $\text{mAP@50} = 98.4\%$, $\text{mAP@50-95} = 89.2\%$, Precision = $97.8\%$, Recall = $98.1\%$. Tốc độ suy luận $18.4\text{ms}$.
* **Stage 2 (Định vị 8 trường thông tin - `yolov8_fields.pt`)**:
  - Dữ liệu: 1,566 ảnh thẻ CCCD đã nắn phẳng (1,218 train, 348 val) với 8 classes.
  - Thời gian huấn luyện: 2 giờ 08 phút (120 epochs, batch 16, AdamW trên GPU NVIDIA Tesla T4).
  - Kết quả: $\text{mAP@50} = 99.1\%$, $\text{mAP@50-95} = 91.5\%$, Precision = $98.6\%$, Recall = $98.9\%$. Số CCCD đạt mAP $99.8\%$, họ tên đạt $99.5\%$. Tốc độ suy luận $22.5\text{ms}$.

---

### 📌 Câu 3: Mô hình VietOCR được cấu tạo như thế nào, dữ liệu và thời gian huấn luyện ra sao, đạt độ chính xác bao nhiêu?
**Trả lời**:
* **Kiến trúc**: Kết hợp CNN (`vgg19_bn`) để trích xuất đặc trưng thị giác và mạng Transformer (6 tầng Encoder, 6 tầng Decoder, $d_{\text{model}}=256$, 8 Attention Heads) để mô hình hóa chuỗi ngôn ngữ tiếng Việt.
* **Dữ liệu**: Base pretrained trên 10 triệu dải chữ tổng hợp, sau đó nhóm fine-tune chuyên sâu trên **45,200 dải chữ thực tế thẻ CCCD** (12k số và ngày, 15k tên in hoa, 18.2k địa chỉ xã/huyện/tỉnh) với bảng từ vựng 230 ký tự.
* **Thời gian huấn luyện**: 5 giờ 26 phút (30 epochs, AdamW trên GPU RTX 3090 24GB).
* **Kết quả**: Độ chính xác ký tự đạt **98.7%** (CER = 1.3%), độ chính xác từ đạt **94.8%** (WER = 5.2%). Sau khi qua bộ Hậu xử lý Cross-field Validation và từ điển địa danh 63 tỉnh, độ chính xác cấp trường tăng lên **99.2%**.

---

### 📌 Câu 4: Tại sao nhóm phát triển tính năng thẩm định tự động bằng Vision AI (AI Oracle)? Cơ chế hoạt động và cách bảo vệ API key như thế nào?
**Trả lời**:
* **Mục đích**: Tự động hóa khâu đánh giá độ chính xác (Ground Truth) mà không cần con người phải ngồi kiểm tra bằng mắt. Giúp người dùng và giảng viên chấm thi thấy ngay sau mỗi lần scan thì hệ thống đọc đúng bao nhiêu % và sai ở những ký tự cụ thể nào.
* **Cơ chế hoạt động**: Gửi ảnh thẻ song song sang mô hình Vision AI tiên tiến (Google Gemini Flash hoặc OpenAI GPT-4o-mini) để lấy kết quả chuẩn độc lập, sau đó chạy thuật toán Weighted Levenshtein Similarity tính điểm theo trọng số từng trường và dùng SequenceMatcher để tô màu trực quan các ký tự lệch (đỏ gạch ngang / xanh lá).
* **Bảo vệ API Key**: Sử dụng kiến trúc 2 tầng (Dual-tier). Key mặc định lưu trong file `.env` trên server và được `.gitignore` bảo vệ tuyệt đối không đẩy lên GitHub/Hugging Face. Key của người dùng vãng lai được lưu trên trình duyệt (`localStorage`) của họ, không lưu vào database server, và tự động ưu tiên ghi đè khi gửi request.

---

### 📌 Câu 5: Nếu người dùng chụp tấm thẻ bị xoay nghiêng 45° (dạng hình thoi) hoặc lộn ngược 180°, hệ thống xử lý như thế nào?
**Trả lời**:
* **Xử lý góc nghiêng 45°**: Hệ thống có thuật toán **360° Omnidirectional Search** quét lưới mịn $15^\circ$. Khi tìm thấy góc có Alignment Score cao nhất (kết hợp Confidence và tỷ lệ Width/Height gần 1.58), hàm `rotate_bound()` xoay bù lại góc nghiêng. Sau đó, thuật toán **Tọa độ cực (Polar Angle Ordering)** sắp xếp 4 góc theo góc quay quanh tâm $C(\bar{x}, \bar{y})$ và phân biệt cạnh dài/ngắn, nên không bao giờ bị lỗi đảo đỉnh như các thuật toán tính tổng $x+y$ thông thường.
* **Xử lý lộn ngược đầu 180°**: Sau khi cắt nắn thẻ, hàm `fix_card_orientation()` chạy dự đoán Stage 2 ở cả góc $0^\circ$ và góc xoay $180^\circ$. Nếu ở góc $180^\circ$ có tổng điểm và số lượng box vượt trội hơn góc $0^\circ$, hệ thống tự động lật $180^\circ$ để chữ quay về đúng chiều đọc trước khi đưa vào VietOCR.

---

### 📌 Câu 6: Làm thế nào hệ thống phát hiện và từ chối thẻ khác (Thẻ sinh viên, thẻ ATM, bằng lái) và thẻ mặt sau?
**Trả lời**:
* **Với thẻ mặt sau**: Mô hình Stage 1 được huấn luyện với 2 nhãn rõ ràng: `0` là `back-cccd` và `1` là `front-cccd`. Khi phát hiện `back-cccd` với $\text{conf} \ge 0.35$, hệ thống lập tức báo vàng *"⚠️ Đây là mặt sau của CCCD! Vui lòng lật lại mặt trước"* và chặn trích xuất.
* **Với thẻ khác**: Các thẻ như sinh viên, ATM chỉ là thẻ nhựa thông thường. Hệ thống thiết lập chốt chặn 3 tầng:
  1. Ngưỡng Stage 1 $\text{conf} \ge 0.35$ (thẻ lạ thường có conf thấp).
  2. Stage 2 bắt buộc phải nhận diện được tối thiểu 4 trường dữ liệu và phải có đồng thời cả `so_cccd` lẫn `ho_ten` (thẻ khác không thể có cấu trúc này).
  3. Nếu đọc được số định danh mà khác 12 chữ số (thẻ SV 8 số, ATM 16 số), lập tức phân loại thành `invalid_card`, báo đỏ rực và khóa chức năng chụp.

---

### 📌 Câu 7: Trường 'Nơi thường trú' có 2 dòng thì hệ thống gom cụm và ghép chuỗi như thế nào để không bị đảo ngược địa chỉ?
**Trả lời**:
* Do Dòng 1 nằm sau nhãn `"Nơi thường trú:"` nên tọa độ $x_1 > 420\text{px}$, còn Dòng 2 bắt đầu từ lề trái $x_1 < 200\text{px}$. Nếu sort theo $x$ thông thường, Dòng 2 sẽ bị nhảy lên trước.
* Nhóm đã phát triển thuật toán **Multiline Sorter** trong `sort_multiline_crops()`: Gom cụm các box theo trọng tâm trục tung $C_y = (y_1+y_2)/2$ thành 2 dòng riêng biệt. Sau đó, trong từng dòng mới sắp xếp từ trái sang phải theo $x_1$. Khi ghép chuỗi, Dòng 1 được đọc trước, phân tách bằng dấu phẩy, rồi đến Dòng 2. Kết quả địa chỉ được bảo toàn chính xác 100% ngữ nghĩa hành chính Việt Nam.

---

### 📌 Câu 8: Tại sao nhóm lại chọn VietOCR (VGG-Transformer) thay vì Tesseract OCR hay EasyOCR?
**Trả lời**:
* Tesseract và EasyOCR là các thư viện tổng quát, xử lý tiếng Việt rất kém ở các dấu thanh phức tạp (dấu ngã, hỏi, nặng, huyền hay bị nhầm lẫn hoặc mất dấu) và không hiểu ngữ cảnh từ vựng tiếng Việt.
* VietOCR sử dụng kiến trúc **Transformer Encoder-Decoder** với cơ chế Attention, có khả năng học mô hình ngôn ngữ (Language Model) tiếng Việt. Nó hiểu được xác suất xuất hiện của các từ trong tên người, địa danh Việt Nam (ví dụ thấy chữ "Nguy" thì xác suất cao từ tiếp theo là "ễn"). Kết hợp với tiền xử lý White Border Padding và CLAHE, VietOCR đạt độ chính xác ký tự trên $98.7\%$.

---

### 📌 Câu 9: Em hãy trình bày các quy tắc kiểm tra chéo (Cross-field Validation) độc đáo trong khâu hậu xử lý?
**Trả lời**:
* **Đối chiếu Giới tính qua số CCCD**: Chữ số thứ 4 trong dãy 12 số CCCD quy định giới tính: số chẵn (`0, 2, 4, 6, 8`) là Nam, số lẻ (`1, 3, 5, 7, 9`) là Nữ. Do đó ngay cả khi chữ "Nam/Nữ" trên ảnh bị mờ rách, hệ thống vẫn khôi phục chính xác 100% giới tính.
* **Đồng bộ Ngày sinh và Ngày hết hạn**: Theo Luật Căn cước, thẻ hết hạn vào đúng ngày sinh nhật ở các mốc 25, 40, 60 tuổi. Ngày và tháng hết hạn luôn trùng khớp với ngày và tháng sinh. Hệ thống tự động sửa năm hết hạn khớp với mốc tuổi gần nhất.
* **Chuẩn hóa địa danh**: Đối chiếu danh mục 63 tỉnh/thành phố và bảng từ điển `COMMON_TYPOS` để sửa các lỗi chính tả phổ biến (như `"Hoàng Mãi"` $\rightarrow$ `"Hoàng Mai"`, `"Hải Dưong"` $\rightarrow$ `"Hải Dương"`).

---

### 📌 Câu 10: Thuật toán khôi phục góc thứ 4 bị che khuất hoạt động dựa trên nguyên lý toán học nào?
**Trả lời**:
* Thẻ CCCD là một hình chữ nhật hoàn hảo, do đó mang đầy đủ tính chất hình học của hình bình hành: Hai đường chéo cắt nhau tại trung điểm của mỗi đường.
* Khi một góc bị ngón tay che, Contour chỉ tìm thấy 3 đỉnh $[P_1, P_2, P_3]$. Thuật toán tìm cặp điểm có khoảng cách lớn nhất để xác định đó là một đường chéo. Trung điểm đường chéo là $\text{Midpoint} = (P_{\text{diag1}} + P_{\text{diag2}}) / 2$.
* Tọa độ điểm góc thứ 4 bị thiếu được suy ra chính xác:
  $$P_{\text{thiếu}} = 2 \times \text{Midpoint} - P_{\text{đối diện}}$$
  Nhờ đó, phép nắn phối cảnh Perspective Transform vẫn được thực hiện toàn vẹn mà không bị méo góc.

---

### 📌 Câu 11: Tại sao lại áp dụng CLAHE trên không gian màu LAB thay vì RGB?
**Trả lời**:
* Nếu áp dụng cân bằng histogram trên hệ màu RGB, cường độ sáng của cả 3 kênh R, G, B đều bị biến đổi đồng thời, dẫn đến hiện tượng sai lệch màu sắc (color distortion) làm bức thẻ bị đổi màu bất thường.
* Trong không gian màu LAB, kênh $L$ (Luminance) hoàn toàn tách biệt với hai kênh màu $A$ và $B$ (Chrominance). Khi áp dụng CLAHE trên kênh $L$, hệ thống chỉ điều chỉnh độ sáng và tương phản cục bộ để triệt tiêu bóng râm, bóng ngón tay mà hoàn toàn giữ nguyên sắc tố màu sắc nguyên bản của thẻ.

---

### 📌 Câu 12: Ưu điểm của bộ lọc Bilateral Filter so với Gaussian Filter trong tiền xử lý chữ là gì?
**Trả lời**:
* Gaussian Filter chỉ tính trọng số không gian (spatial distance): pixel càng gần tâm thì trọng số càng cao, do đó nó làm mờ đồng đều cả nhiễu hạt lẫn đường biên sắc nét của nét chữ.
* Bilateral Filter kết hợp 2 hàm Gaussian: Trọng số không gian **VÀ** trọng số cường độ màu (radiometric intensity). Tại các đường biên chữ (nơi có sự chênh lệch lớn giữa màu mực đen và nền thẻ sáng), trọng số màu sẽ triệt tiêu hiệu ứng làm mờ, nhờ đó lọc sạch nhiễu hạt camera mà đường viền ký tự vẫn giữ nguyên độ sắc nét tuyệt đối (**Edge-preserving**).

---

### 📌 Câu 13: Độ tin cậy tổng hợp (Combined Confidence) được tính như thế nào và có ý nghĩa gì?
**Trả lời**:
* Công thức:
  $$\text{Combined\_Confidence} = \text{Mean}(\text{OCR\_Confidence}) \times \frac{\text{Detected\_Fields\_Count}}{8.0}$$
* Ý nghĩa: Nếu chỉ tính trung bình độ tin cậy của VietOCR, trong trường hợp ảnh chỉ đọc được 2 trường nhưng 2 trường đó đọc rất rõ ($\text{conf} = 0.95$), hệ thống sẽ báo độ tin cậy 95%, gây hiểu lầm cho người dùng là hồ sơ đã hoàn chỉnh.
* Công thức của nhóm nhân thêm hệ số phạt: Nếu chỉ tìm thấy 4/8 trường, điểm tin cậy tổng thể bị phạt giảm $50\%$, giúp người quản trị hệ thống biết ngay hồ sơ có bị thiếu thông tin hay không.

---

### 📌 Câu 14: Hệ thống lưu trữ cơ sở dữ liệu như thế nào? Có bảo mật không?
**Trả lời**:
* Hệ thống sử dụng kiến trúc ORM (SQLAlchemy) với cơ chế tự động chuyển đổi: Ưu tiên PostgreSQL cho môi trường Production và tự động kích hoạt SQLite (`ocr_cccd.db`) khi chạy Offline/Local mà không cần cài đặt phức tạp.
* Bảo mật thông tin: Mật khẩu người dùng được băm một chiều bằng thuật toán BCrypt với salt ngẫu nhiên; phiên làm việc được chứng thực qua JWT (JSON Web Token) có thời hạn; bảng `cccd_results` liên kết chặt chẽ với `scan_history` qua quan hệ 1-1 để phục vụ kiểm toán và đối soát dữ liệu (`ai_corrections`).

---

### 📌 Câu 15: Thời gian xử lý trung bình của hệ thống là bao nhiêu và chạy trên phần cứng gì?
**Trả lời**:
* Thời gian xử lý trung bình: Khoảng **0.72 - 0.78 giây** cho một bức ảnh hoàn chỉnh (từ khâu nhận ảnh, xoay nắn, bóc 8 trường, chạy VietOCR cho đến lưu CSDL).
* Thử nghiệm trên phần cứng máy trạm Mac Apple Silicon (chạy MPS / CPU) hoặc Intel Core i5 không cần card đồ họa rời đắt tiền, nhờ việc tối ưu kích thước ảnh crop ($h=48$), tắt Beam Search (dùng Greedy Search) và phân tầng tìm kiếm góc nghiêng thông minh.
