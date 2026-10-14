# backend/main.py
import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Add root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.api import api_router, ocr_router

app = FastAPI(
    title="CCCD OCR API Service",
    description="Hệ thống AI nhận diện và trích xuất dữ liệu CCCD (YOLOv8 + VietOCR + PostgreSQL)",
    version="2.0.0"
)

# 1. Cấu hình CORS cho phép React frontend kết nối
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Đăng ký các Router REST API
app.include_router(api_router)
app.include_router(ocr_router)

# 3. Mount thư mục media tĩnh
Path("data/output").mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory="data/output"), name="media")

# Mount static build nếu frontend/dist đã được build
dist_path = ROOT_DIR / "frontend" / "dist"
if (dist_path / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(dist_path / "assets")), name="assets")

# 4. Phục vụ giao diện trang chủ
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    # Ưu tiên frontend/dist/index.html nếu đã build production
    if (dist_path / "index.html").exists():
        return FileResponse(dist_path / "index.html")
    
    # Dự phòng template HTML
    template_path = ROOT_DIR / "frontend" / "templates" / "index.html"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    
    return HTMLResponse("<h1>CCCD OCR API is running</h1>")


if __name__ == "__main__":
    import uvicorn
    is_container = os.environ.get("SPACE_ID") or os.environ.get("CONTAINER") or os.path.exists("/.dockerenv")
    default_host = "0.0.0.0" if is_container else "127.0.0.1"
    host = os.environ.get("HOST", default_host)
    port = int(os.environ.get("PORT", 8000))
    reload = os.environ.get("RELOAD", "false").lower() == "true"
    
    print("\n" + "="*60)
    print("🚀 CCCD OCR BACKEND SERVER ĐANG KHỞI CHẠY!")
    print(f"👉 Vui lòng mở trình duyệt tại: http://127.0.0.1:{port} hoặc http://localhost:{port}")
    print(f"⚠️  LƯU Ý: Không dùng http://0.0.0.0:{port} vì Chrome sẽ chặn Camera ('Not Secure').")
    print("="*60 + "\n")
    
    uvicorn.run("backend.main:app", host=host, port=port, reload=reload)
