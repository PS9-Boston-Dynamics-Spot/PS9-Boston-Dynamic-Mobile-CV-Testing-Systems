from ultralytics import YOLO
from PIL import Image
from pathlib import Path

# Modell laden
model = YOLO('yolov8n.pt')  #best.pt für trainiertes Modell verwenden

# Pfade
raw_dir = Path('data/images/raw')
crop_dir = Path('data/images/crops')
label_dir = Path('data/labels/train')

crop_dir.mkdir(parents=True, exist_ok=True)
label_dir.mkdir(parents=True, exist_ok=True)
# Erkennung, Cropping, Resizing & Labeling
for img_path in raw_dir.glob('*.jpg'):
    results = model(img_path)
    im = Image.open(img_path).convert("RGB")
    width, height = im.size
    
    label_path = label_dir / f"{img_path.stem}.txt"
    with open(label_path, "w") as f:
        for box, cls in zip(results[0].boxes.xyxy, results[0].boxes.cls):
            x1, y1, x2, y2 = map(float, box)

            # Begrenzen auf Bildgrenzen
            x1 = max(0, int(x1))
            y1 = max(0, int(y1))
            x2 = min(width, int(x2))
            y2 = min(height, int(y2))

            # Nur croppen, wenn Box größer als 0 ist
            if x2 > x1 and y2 > y1:
                crop = im.crop((x1, y1, x2, y2)).resize((224, 224))
                crop.save(crop_dir / f"{img_path.stem}_crop_{int(cls.item())}.jpg")

            # YOLO-Label schreiben (normalisiert)
            x_center = ((x1 + x2) / 2) / width
            y_center = ((y1 + y2) / 2) / height
            w = (x2 - x1) / width
            h = (y2 - y1) / height
            class_id = int(cls.item())
            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}\n")

print("CHECK: Labels und Crops erfolgreich erstellt!")
