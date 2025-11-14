from ultralytics import YOLO
from PIL import Image
from pathlib import Path

# Modell laden
model = YOLO('runs/detect/train/weights/best.pt')

# Pfade
# Ausgangsverzeichnis für Rohbilder
raw_dir = Path('data/images/raw')
# Zielverzeichnis für zugeschnittene und resized Bilder
crop_dir = Path('data/images/crops')
# Sicherstellen, dass das Zielverzeichnis existiert
crop_dir.mkdir(parents=True, exist_ok=True)

# Erkennung, Cropping und Resizing
for img_path in raw_dir.glob('*.jpg'):
    results = model(img_path)
    im = Image.open(img_path).convert("RGB")

    for i, box in enumerate(results[0].boxes.xyxy):
        x1, y1, x2, y2 = map(int, box)
        crop = im.crop((x1, y1, x2, y2))
        crop = crop.resize((224, 224))  # direkt resized
        crop.save(crop_dir / f"{img_path.stem}_crop{i}.jpg")

print("✅ Alle Anzeigen erkannt, zugeschnitten & resized gespeichert.")
