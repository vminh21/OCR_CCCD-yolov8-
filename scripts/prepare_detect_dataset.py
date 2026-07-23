"""
Validate images/labels and create train/val/test splits.
Usage:
  python scripts/prepare_detect_dataset.py --src data/cccd_detect --out data/cccd_detect

This script assumes you have all images under data/cccd_detect/images/all_images
and labels under data/cccd_detect/labels/all_labels (matching filenames). It will
shuffle and split into train/val/test and copy files into images/train, labels/train, etc.
"""
import argparse
from pathlib import Path
import shutil
import random


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', default='data/cccd_detect')
    parser.add_argument('--out', default='data/cccd_detect')
    parser.add_argument('--train', type=float, default=0.8)
    parser.add_argument('--val', type=float, default=0.1)
    parser.add_argument('--test', type=float, default=0.1)
    args = parser.parse_args()

    src = Path(args.src)
    images_all = src / 'images' / 'all_images'
    labels_all = src / 'labels' / 'all_labels'
    if not images_all.exists() or not labels_all.exists():
        print('Expected dataset layout with all_images and all_labels folders.')
        return

    images = [p for p in images_all.glob('*') if p.suffix.lower() in ['.jpg', '.jpeg', '.png']]
    random.shuffle(images)

    n = len(images)
    n_train = int(n * args.train)
    n_val = int(n * args.val)

    splits = {
        'train': images[:n_train],
        'val': images[n_train:n_train + n_val],
        'test': images[n_train + n_val:]
    }

    for split, items in splits.items():
        out_img_dir = src / 'images' / split
        out_lbl_dir = src / 'labels' / split
        out_img_dir.mkdir(parents=True, exist_ok=True)
        out_lbl_dir.mkdir(parents=True, exist_ok=True)

        for img_path in items:
            stem = img_path.stem
            # find corresponding txt
            label_path = labels_all / (stem + '.txt')
            if not label_path.exists():
                print('Warning: label missing for', img_path.name)
                continue
            shutil.copy(img_path, out_img_dir / img_path.name)
            shutil.copy(label_path, out_lbl_dir / (stem + '.txt'))

        print(f'Prepared {len(list(out_img_dir.glob("*")))} images for {split}')

if __name__ == '__main__':
    main()
