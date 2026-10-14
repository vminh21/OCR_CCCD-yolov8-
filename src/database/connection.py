# src/database/connection.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

Base = declarative_base()

def init_engine():
    raw_db_url = os.getenv("DATABASE_URL")
    
    # 1. Thử kết nối PostgreSQL nếu được cấu hình
    if raw_db_url and raw_db_url.startswith("postgresql"):
        try:
            eng = create_engine(
                raw_db_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                connect_args={"connect_timeout": 3}
            )
            with eng.connect() as conn:
                pass
            print("✅ Đã kết nối cơ sở dữ liệu PostgreSQL thành công!")
            return eng
        except Exception as e:
            print(f"ℹ️ Không thể kết nối PostgreSQL ({e}). Tự động kích hoạt SQLite.")
    
    # 2. Tự động dùng SQLite cục bộ (Chạy hoàn hảo trên Hugging Face Spaces & Local)
    db_file = os.path.abspath("ocr_cccd.db")
    sqlite_url = f"sqlite:///{db_file}"
    eng = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False}
    )
    print(f"✅ Đã khởi tạo cơ sở dữ liệu SQLite: {sqlite_url}")
    return eng

engine = init_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tự động tạo bảng nếu chưa tồn tại
try:
    import src.database.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"[DB Notice] create_all: {e}")

def get_db():
    """FastAPI Dependency cung cấp Session cơ sở dữ liệu cho mỗi request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
