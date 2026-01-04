import cv2
import pytesseract
from pathlib import Path
from ultralytics import YOLO
import numpy as np

# -------------------------------------------------
# Konfiguration
# -------------------------------------------------

RAW_DIR = Path("/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/Data/images/raw")
CROP_DIR = Path("/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/Data/images/crop")
CROP_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = "runs_display/spot_v12/weights/best.pt"

CLASS_META = {
    0: {"sensor_type": "digital", "category": "temperature", "unit": "°C"},
    1: {"sensor_type": "digital", "category": "temperature", "unit": "°C"},
}

# -------------------------------------------------
# Initialisierung
# -------------------------------------------------

model = YOLO(MODEL_PATH)

# -------------------------------------------------
# Hilfsfunktionen
# -------------------------------------------------

def crop_and_quality(img, box):
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    crop = img[y1:y2, x1:x2]

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    quality = min(lap_var / 500.0, 1.0)

    return crop, quality

def extract_value_tesseract(crop):
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    _, thresh = cv2.threshold(gray, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    config = "--psm 7 -c tessedit_char_whitelist=0123456789.-"
    text = pytesseract.image_to_string(thresh, config=config)

    try:
        return float(text.strip()), text.strip()
    except ValueError:
        return None, text.strip()

# -------------------------------------------------
# Hauptpipeline
# -------------------------------------------------

def process_images():
    for img_path in RAW_DIR.glob("*.jpg"):
        img = cv2.imread(str(img_path))
        results = model(img, conf=0.3)[0]

        for i, box in enumerate(results.boxes):
            cls_id = int(box.cls)
            meta = CLASS_META.get(cls_id)

            if meta is None:
                continue

            crop, quality = crop_and_quality(img, box)
            value, raw_text = extract_value_tesseract(crop)

            crop_name = f"{img_path.stem}_det{i}_cls{cls_id}"
            crop_img_path = CROP_DIR / f"{crop_name}.jpg"
            crop_txt_path = CROP_DIR / f"{crop_name}.txt"

            cv2.imwrite(str(crop_img_path), crop)

            with open(crop_txt_path, "w") as f:
                f.write(f"source_image: {img_path.name}\n")
                f.write(f"class_id: {cls_id}\n")
                f.write(f"sensor_type: {meta['sensor_type']}\n")
                f.write(f"category: {meta['category']}\n")
                f.write(f"unit: {meta['unit']}\n")
                f.write(f"quality: {quality:.3f}\n")
                f.write(f"ocr_raw_text: '{raw_text}'\n")
                f.write(f"value: {value}\n")

            print(f"[OK] Crop gespeichert: {crop_img_path.name}")

# -------------------------------------------------
# Start
# -------------------------------------------------

if __name__ == "__main__":
    process_images()
