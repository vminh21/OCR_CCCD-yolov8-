"""
Visualize YOLO boxes on images for sanity checks.
Usage:
  python scripts/visualize_boxes.py --image input/cccd3.jpg --label data/cccd_detect/labels/train/cccd3.txt
"""
import argparse
import cv2
from pathlib import Path


def yolo_to_bbox(line, img_w, img_h):
    parts = line.strip().split()
    cls = int(parts[0])
    x_c, y_c, w, h = map(float, parts[1:5])
    x_c *= img_w
    y_c *= img_h
    w *= img_w
    h *= img_h
    x1 = int(x_c - w/2)
    y1 = int(y_c - h/2)
    x2 = int(x_c + w/2)
    y2 = int(y_c + h/2)
    return x1, y1, x2, y2, cls


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', required=True)
    parser.add_argument('--label', required=True)
    parser.add_argument('--out', default='viz_out.jpg')
    args = parser.parse_args()

    img = cv2.imread(args.image)
    h, w = img.shape[:2]
    with open(args.label, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    for l in lines:
        x1, y1, x2, y2, cls = yolo_to_bbox(l, w, h)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(img, str(cls), (x1, max(0,y1-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    cv2.imwrite(args.out, img)
    print('Wrote', args.out)

if __name__ == '__main__':
    main()
