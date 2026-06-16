from pathlib import Path
from src.pipeline import process_cccd

SUPPORTED_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
)

def main():
    input_dir = Path("input")
    if not input_dir.exists():
        print("Không tìm thấy thư mục input/")
        return

    image_files = []

    for ext in SUPPORTED_EXTENSIONS:
        image_files.extend(
            input_dir.glob(f"*{ext}")
        )

    if not image_files:
        print("Không có ảnh trong thư mục input/")
        return

    print(" OCR CCCD SYSTEM ")
    print(f"\nTìm thấy {len(image_files)} ảnh\n")

    success = 0

    for idx, image_path in enumerate(image_files, start=1):
        print("\n" + "=" * 60)
        print(f"[{idx}/{len(image_files)}]")
        print(f"Ảnh: {image_path.name}")
        print("=" * 60)

        try:
            result = process_cccd(
                str(image_path)
            )
            success += 1
            print("\nThành công")
        except Exception as e:
            print("\nLỗi")
            import traceback
            traceback.print_exc()
    print("\n")
    print("=" * 60)
    print("TỔNG KẾT")
    print("=" * 60)
    print(f"Tổng số ảnh : {len(image_files)}")
    print(f"Thành công  : {success}")
    print(f"Thất bại    : {len(image_files)-success}")

if __name__ == "__main__":
    main()