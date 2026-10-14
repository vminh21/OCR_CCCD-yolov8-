# main.py - Root entrypoint forwarding to backend.main
import os
import uvicorn
from backend.main import app

if __name__ == "__main__":
    is_container = os.environ.get("SPACE_ID") or os.environ.get("CONTAINER") or os.path.exists("/.dockerenv")
    default_host = "0.0.0.0" if is_container else "127.0.0.1"
    host = os.environ.get("HOST", default_host)
    port = int(os.environ.get("PORT", 8000))
    reload = os.environ.get("RELOAD", "false").lower() == "true"
    
    print("\n" + "="*60)
    print("🚀 CCCD OCR SERVER ĐANG KHỞI CHẠY!")
    print(f"👉 Vui lòng mở trình duyệt tại: http://127.0.0.1:{port} hoặc http://localhost:{port}")
    print(f"⚠️  LƯU Ý: Không dùng http://0.0.0.0:{port} vì Chrome sẽ chặn Camera ('Not Secure').")
    print("="*60 + "\n")
    
    uvicorn.run("backend.main:app", host=host, port=port, reload=reload)