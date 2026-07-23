"""
Simple training script for YOLOv8 detect model using ultralytics.

Usage:
  python scripts/detect_train.py --data data/cccd_detect.yaml --epochs 50

This script assumes you have data organized in YOLO format (images + labels).
See `data/cccd_detect.yaml` for expected layout.
"""
import argparse
from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='data/detect_card/id-card-side-object-detection.v1i.yolov8/data.yaml')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--batch', type=int, default=8)
    parser.add_argument('--device', default='cpu')
    args = parser.parse_args()

    # load a pretrained small model
    model = YOLO('yolov8n.pt')

    # train
    model.train(data=args.data, epochs=args.epochs, imgsz=args.imgsz, batch=args.batch, device=args.device)

    # save best model to repo models/
    model.export(format='pt')
    print('Training finished. Exported model to working dir (check ultralytics outputs).')


if __name__ == '__main__':
    main()
