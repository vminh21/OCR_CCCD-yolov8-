# test_batch.py
import sys
import time
from pathlib import Path

# Thêm đường dẫn root vào sys.path
sys.path.append(str(Path(__file__).resolve().parent))

from src.core.pipeline import process_cccd
from config.settings import INPUT_DIR


def run_batch_test(input_folder=INPUT_DIR):
    """Đánh giá hiệu năng và chạy thử nghiệm hàng loạt trên một thư mục ảnh."""
    input_path = Path(input_folder)
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

    if not input_path.exists():
        print(f"❌ Lỗi: Không tìm thấy thư mục {input_folder}")
        return

    image_files = [f for f in input_path.iterdir() if f.suffix.lower() in valid_extensions]

    if not image_files:
        print(f"⚠️ Không tìm thấy ảnh nào trong {input_folder}")
        return

    print(f"🔍 Tìm thấy {len(image_files)} ảnh trong {input_folder}")

    success_count = 0
    start_time = time.time()

    for img_path in image_files:
        try:
            result = process_cccd(str(img_path))
            if result is not None:
                success_count += 1
        except Exception as e:
            print(f"❌ Lỗi khi xử lý {img_path.name}: {e}")

    total_time = time.time() - start_time

    print("\n" + "=" * 40)
    print("📊 BÁO CÁO KẾT QUẢ BATCH TEST (YOLOV8 + VIETOCR)")
    print("=" * 40)
    print(f"Tổng số ảnh       : {len(image_files)}")
    print(f"Xử lý thành công   : {success_count}/{len(image_files)}")
    print(f"Thời gian tổng    : {total_time:.2f}s")
    print(f"Tốc độ trung bình : {total_time / len(image_files):.2f}s/ảnh")
    print("=" * 40 + "\n")


if __name__ == "__main__":
    run_batch_test()