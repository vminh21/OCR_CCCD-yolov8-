"""
Convert Pascal VOC XML annotations to YOLO txt format.
Usage:
  python scripts/convert_annotations.py --images data/cccd_detect/images/train --xmls path_to_xmls --out data/cccd_detect/labels/train
"""
import os
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


def voc_to_yolo(xml_path, img_w, img_h):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    yolo_lines = []
    for obj in root.findall('object'):
        cls_name = obj.find('name').text
        # for this dataset assume single class -> id 0
        cls_id = 0
        bndbox = obj.find('bndbox')
        xmin = float(bndbox.find('xmin').text)
        ymin = float(bndbox.find('ymin').text)
        xmax = float(bndbox.find('xmax').text)
        ymax = float(bndbox.find('ymax').text)
        x_center = ((xmin + xmax) / 2.0) / img_w
        y_center = ((ymin + ymax) / 2.0) / img_h
        w = (xmax - xmin) / img_w
        h = (ymax - ymin) / img_h
        yolo_lines.append(f"{cls_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}")
    return yolo_lines


def get_image_size(image_path):
    import cv2
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")
    h, w = img.shape[:2]
    return w, h


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--images', required=True)
    parser.add_argument('--xmls', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()

    images_dir = Path(args.images)
    xmls_dir = Path(args.xmls)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    for xml_file in xmls_dir.glob('*.xml'):
        stem = xml_file.stem
        # try to find corresponding image in images_dir
        img_path = None
        for ext in ['.jpg', '.jpeg', '.png']:
            candidate = images_dir / (stem + ext)
            if candidate.exists():
                img_path = candidate
                break
        if img_path is None:
            print(f'Skip {xml_file}: no image found')
            continue
        w, h = get_image_size(img_path)
        yolo_lines = voc_to_yolo(xml_file, w, h)
        out_path = out_dir / (stem + '.txt')
        with open(out_path, 'w') as f:
            f.write('\n'.join(yolo_lines))
        print('Converted', xml_file, '->', out_path)

if __name__ == '__main__':
    main()
