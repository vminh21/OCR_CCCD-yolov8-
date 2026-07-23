# test_batch.py
import os
import time
from pathlib import Path
from src.pipeline_v2 import process_cccd

def run_batch_test(input_folder):
    input_path = Path(input_folder)
    valid_extensions = {'.jpg', '.jpeg', '.png'}
    
    # Lấy danh sách ảnh
    image_files = [f for f in input_path.iterdir() if f.suffix.lower() in valid_extensions]
    
    print(f"🔍 Tìm thấy {len(image_files)} ảnh trong {input_folder}")
    
    success_count = 0
    start_time = time.time()

    for img_path in image_files:
        try:
            # Chạy pipeline, nếu không bị lỗi (None) thì cộng 1
            result = process_cccd(str(img_path))
            if result is not None:
                success_count += 1
        except Exception as e:
            print(f"❌ Lỗi văng app khi xử lý {img_path.name}: {e}")

    total_time = time.time() - start_time
    
    print("\n" + "="*40)
    print("📊 BÁO CÁO BATCH TEST")
    print("="*40)
    print(f"Tổng số ảnh: {len(image_files)}")
    print(f"Xử lý thành công: {success_count}/{len(image_files)}")
    print(f"Thời gian tổng: {total_time:.2f}s")
    print(f"Tốc độ trung bình: {total_time/len(image_files):.2f}s/ảnh")

if __name__ == "__main__":
    # Trỏ vào thư mục chứa ảnh val hoặc test của bạn
    run_batch_test("data/detect_card/images/val")