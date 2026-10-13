# ==============================================================
# Dockerfile chuẩn cho Hugging Face Spaces (Port 7860, User 1000)
# ==============================================================
FROM python:3.10-slim

# Ngăn Python tạo bytecode .pyc và hiển thị log trực tiếp
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Cài đặt các thư viện hệ thống cần thiết cho OpenCV và build C-extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập người dùng non-root (UID 1000) theo chuẩn Hugging Face Spaces
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    HOST=0.0.0.0 \
    PORT=7860

WORKDIR $HOME/app

# Sao chép và cài đặt các thư viện Python
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Sao chép toàn bộ mã nguồn ứng dụng
COPY --chown=user . $HOME/app

# Tạo sẵn thư mục weights và data với quyền user 1000
RUN mkdir -p $HOME/app/weights $HOME/app/data

# Hugging Face Spaces tự động map traffic vào cổng 7860
EXPOSE 7860

# Khởi chạy ứng dụng
CMD ["python3", "main.py"]
