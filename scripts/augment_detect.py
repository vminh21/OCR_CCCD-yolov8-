"""
Augment detection dataset with albumentations while preserving bounding boxes (YOLO format conversion).
Usage:
  python scripts/augment_detect.py --images data/cccd_detect/images/train --labels data/cccd_detect/labels/train --out images_aug labels_aug --n 3

This script reads YOLO txt labels, converts them to pascal bbox, applies augmentation,
then writes new images and YOLO labels.
"""
import argparse
from pathlib import Path
import cv2
import albumentations as A
import os


def yolo_to_bbox(line, img_w, img_h):
    parts = line.strip().split()
    cls = parts[0]
    x_c, y_c, w, h = map(float, parts[1:5])
    x_c *= img_w
    y_c *= img_h
    w *= img_w
    h *= img_h
    x1 = int(x_c - w/2)
    y1 = int(y_c - h/2)
    x2 = int(x_c + w/2)
    y2 = int(y_c + h/2)
    return [x1, y1, x2, y2, int(cls)]


def bbox_to_yolo(bbox, img_w, img_h):
    x1, y1, x2, y2, cls = bbox
    w = x2 - x1
    h = y2 - y1
    x_c = x1 + w/2
    y_c = y1 + h/2
    return f"{cls} {x_c/img_w:.6f} {y_c/img_h:.6f} {w/img_w:.6f} {h/img_h:.6f}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--images', required=True)
    parser.add_argument('--labels', required=True)
    parser.add_argument('--out_images', required=True)
    parser.add_argument('--out_labels', required=True)
    parser.add_argument('--n', type=int, default=3)
    args = parser.parse_args()

    images_dir = Path(args.images)
    labels_dir = Path(args.labels)
    out_images = Path(args.out_images)
    out_labels = Path(args.out_labels)
    out_images.mkdir(parents=True, exist_ok=True)
    out_labels.mkdir(parents=True, exist_ok=True)

    transform = A.Compose([
        A.OneOf([
            A.RandomBrightnessContrast(p=0.6),
            A.CLAHE(p=0.6),
        ], p=0.7),
        A.Rotate(limit=15, border_mode=cv2.BORDER_CONSTANT, p=0.6),
        A.OneOf([A.GaussNoise(p=0.3), A.ISONoise(p=0.3)], p=0.5),
        A.MotionBlur(blur_limit=3, p=0.3),
    ], bbox_params=A.BboxParams(format='pascal_voc', label_fields=['category_ids']))

    for img_path in images_dir.glob('*'):
        if img_path.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
            continue
        stem = img_path.stem
        lbl_path = labels_dir / (stem + '.txt')
        if not lbl_path.exists():
            print('skip, no label for', img_path)
            continue
        img = cv2.imread(str(img_path))
        h, w = img.shape[:2]
        with open(lbl_path, 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
        bboxes = []
        category_ids = []
        for l in lines:
            bb = yolo_to_bbox(l, w, h)
            bboxes.append(bb[:4])
            category_ids.append(int(bb[4]))
        
        for i in range(args.n):
            try:
                augmented = transform(image=img, bboxes=bboxes, category_ids=category_ids)
            except Exception as e:
                print('aug error', e)
                continue
            aug_img = augmented['image']
            aug_bboxes = augmented['bboxes']
            out_name = f"{stem}_aug_{i}.jpg"
            cv2.imwrite(str(out_images / out_name), aug_img)
            # write yolo label
            with open(out_labels / (stem + f'_aug_{i}.txt'), 'w') as fo:
                for idx, bb in enumerate(aug_bboxes):
                    x1, y1, x2, y2 = map(int, bb)
                    yolo_line = bbox_to_yolo([x1, y1, x2, y2, category_ids[idx]], aug_img.shape[1], aug_img.shape[0])
                    fo.write(yolo_line + '\n')
            print('wrote', out_name)

if __name__ == '__main__':
    main()
