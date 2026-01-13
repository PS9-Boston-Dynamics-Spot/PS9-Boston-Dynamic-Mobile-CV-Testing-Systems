from ultralytics import YOLO
from PIL import Image
from pathlib import Path

Image.MAX_IMAGE_PIXELS = None

# Eigenes Modell (4 Klassen)
model = YOLO("runs/detect/train12/weights/best.pt")

img_dir = Path("data/images/train")
label_dir = Path("data/labels/train")
label_dir.mkdir(parents=True, exist_ok=True)

for img_path in img_dir.glob("*.jpg"):
    results = model(img_path)
    im = Image.open(img_path)
    w, h = im.size

    label_file = label_dir / f"{img_path.stem}.txt"
    with open(label_file, "w") as f:
        for box, cls in zip(results[0].boxes.xyxy, results[0].boxes.cls):
            x1, y1, x2, y2 = box
            x_center = ((x1 + x2) / 2) / w
            y_center = ((y1 + y2) / 2) / h
            bw = (x2 - x1) / w
            bh = (y2 - y1) / h
            class_id = int(cls.item())
            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {bw:.6f} {bh:.6f}\n")

print("✅ Alle Pseudo-Labels mit korrekten Klassen-IDs (0–3) erstellt.")
