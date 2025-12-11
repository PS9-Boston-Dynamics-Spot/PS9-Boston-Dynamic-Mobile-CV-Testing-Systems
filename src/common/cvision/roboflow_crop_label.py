import os
import cv2
import base64
import requests
import json
import csv
from pathlib import Path

# -----------------------------
# CONFIG – Pfade dynamisch aus Projektstruktur ableiten
# -----------------------------
# roboflow_crop_label.py liegt unter: src/common/cvision
# -> 3 Ebenen hoch = Projektroot
project_root = Path(__file__).resolve().parents[3]

RAW_FOLDER = project_root / "data" / "images" / "raw"
CROP_FOLDER = project_root / "data" / "images" / "crop"
CSV_PATH = project_root / "data" / "labels" / "roboflow_predictions.csv"

WORKSPACE = "ps-9"
WORKFLOW_ID = "find-digitaldisplayofenacs-digitaldisplaytemperatures-and-analogdisplaypressures"
API_URL = f"https://serverless.roboflow.com/{WORKSPACE}/workflows/{WORKFLOW_ID}"

# 🔐 API-Key besser aus Umgebung lesen; zur Not hartkodiert:
API_KEY = os.getenv("ROBOFLOW_API_KEY", "RYmNlhCjTmyi92J0pOwr")

# -----------------------------
# Create folders if missing
# -----------------------------
CROP_FOLDER.mkdir(parents=True, exist_ok=True)
CSV_PATH.parent.mkdir(parents=True, exist_ok=True)


def run_roboflow_inference(image_path: str):
    """Send image to Roboflow workflow and return predictions."""
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "api_key": API_KEY,
        "inputs": {
            "image": {
                "type": "base64",
                "value": b64
            }
        }
    }

    response = requests.post(API_URL, json=payload)
    response.raise_for_status()
    return response.json()


def append_prediction_to_csv(original_image: str, crop_filename: str, pred: dict):
    """
    Speichert eine einzelne Bounding-Box-Prediction in der CSV-Datei.

    WICHTIG:
    - display_type = "analog" oder "digital"
    - anhand des Roboflow-Klassennamens (pred["class"])
    """
    file_exists = CSV_PATH.is_file()

    class_raw = pred.get("class", "")
    class_lower = class_raw.lower()

    # Mapping: analog vs digital
    if "analog" in class_lower:
        display_type = "analog"
    elif "digital" in class_lower:
        display_type = "digital"
    else:
        display_type = "unknown"  # falls mal was anderes kommt

    with CSV_PATH.open("a", newline="") as f:
        writer = csv.writer(f, delimiter=';')

        # Header nur einmal schreiben
        if not file_exists:
            writer.writerow([
                "original_image",
                "crop_image",
                "class_raw",     # original Roboflow-Klasse
                "display_type",  # analog / digital
                "confidence",
                "x_center",
                "y_center",
                "width",
                "height"
            ])

        writer.writerow([
            original_image,
            crop_filename,
            class_raw,         # z.B. "analogdisplaypressures"
            display_type,      # "analog" oder "digital"
            pred.get("confidence", 0.0),
            pred.get("x", 0.0),
            pred.get("y", 0.0),
            pred.get("width", 0.0),
            pred.get("height", 0.0),
        ])


def crop_predictions(image_path: Path, predictions: list):
    """Crop detected bounding boxes and store in images/crop folder + schreibe CSV."""

    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Bild konnte nicht geladen werden: {image_path}")

    h, w, _ = img.shape
    base_name = image_path.stem

    for i, pred in enumerate(predictions):
        x, y = pred["x"], pred["y"]
        pw, ph = pred["width"], pred["height"]

        # Roboflow liefert bounding boxes im Mittelpunkt (x,y)
        x1 = int(x - pw / 2)
        y1 = int(y - ph / 2)
        x2 = int(x + pw / 2)
        y2 = int(y + ph / 2)

        # Clipping auf Bildgrenzen
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)

        crop = img[y1:y2, x1:x2]

        if crop.size == 0:
            print(f"⚠️ Prediction {i} ergibt kein gültiges Crop - übersprungen.")
            continue

        crop_filename = f"{base_name}_crop_{i}.jpg"
        full_path = CROP_FOLDER / crop_filename

        cv2.imwrite(str(full_path), crop)
        print(f"📸 Crop gespeichert: {full_path}")

        # ➕ CSV-Eintrag für diese Bounding Box
        append_prediction_to_csv(
            original_image=image_path.name,
            crop_filename=crop_filename,
            pred=pred
        )


def process_all_images():
    """Processes every image in images/raw and saves crops + CSV-Labels."""
    if not RAW_FOLDER.exists():
        print(f"❌ RAW_FOLDER existiert nicht: {RAW_FOLDER}")
        return

    files = [p for p in RAW_FOLDER.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png")]

    if not files:
        print(f"❌ Keine Bilder im Ordner: {RAW_FOLDER}")
        return

    print(f"📝 CSV wird geschrieben nach: {CSV_PATH}")

    for image_path in files:
        print(f"\n🔍 Verarbeite Datei: {image_path}")

        # Schritt 1: Roboflow ausführen
        result = run_roboflow_inference(str(image_path))

        # Schritt 2: Predictions aus Result extrahieren
        # (Struktur abhängig vom Workflow – hier wie in deinem Beispiel)
        predictions = result["outputs"][0]["predictions"]["predictions"]

        print(f"➡️ {len(predictions)} Bildschirme erkannt.")

        # Schritt 3: Croppen + CSV
        crop_predictions(image_path, predictions)

    print("\n✅ Fertig! Crops in images/crop gespeichert und Labels in CSV geschrieben.")


if __name__ == "__main__":
    process_all_images()
