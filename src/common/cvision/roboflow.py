import os
import cv2
import base64
import requests
import json

# -----------------------------
# CONFIG
# -----------------------------
projectdir = "/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems"
RAW_FOLDER = f"{projectdir}/data/images/raw"
CROP_FOLDER = f"{projectdir}/data/images/crop"

WORKSPACE = "ps-9"
WORKFLOW_ID = "find-digitaldisplayofenacs-digitaldisplaytemperatures-and-analogdisplaypressures"
API_URL = f"https://serverless.roboflow.com/{WORKSPACE}/workflows/{WORKFLOW_ID}"
API_KEY = "RYmNlhCjTmyi92J0pOwr"  # <-- Setze diese Umgebungsvariable! :ROBOFLOW_API_KEY

# -----------------------------
# Create crop folder if missing
# -----------------------------
os.makedirs(CROP_FOLDER, exist_ok=True)

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

def crop_predictions(image_path: str, predictions: list):
    """Crop detected bounding boxes and store in images/crop folder."""

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Bild konnte nicht geladen werden: {image_path}")

    h, w, _ = img.shape
    base_name = os.path.splitext(os.path.basename(image_path))[0]

    for i, pred in enumerate(predictions):
        x, y = pred["x"], pred["y"]
        pw, ph = pred["width"], pred["height"]

        # Roboflow liefert bounding boxes im Mittelpunkt
        x1 = int(x - pw / 2)
        y1 = int(y - ph / 2)
        x2 = int(x + pw / 2)
        y2 = int(y + ph / 2)

        # Clipping
        x1 = max(0, x1); y1 = max(0, y1)
        x2 = min(w, x2); y2 = min(h, y2)

        crop = img[y1:y2, x1:x2]

        if crop.size == 0:
            print(f"⚠️ Prediction {i} ergibt kein gültiges Crop - übersprungen.")
            continue

        crop_filename = f"{CROP_FOLDER}/{base_name}_crop_{i}.jpg"
        cv2.imwrite(crop_filename, crop)
        print(f"📸 Crop gespeichert: {crop_filename}")


def process_all_images():
    """Processes every image in images/raw and saves crops."""
    files = [f for f in os.listdir(RAW_FOLDER) if f.lower().endswith((".jpg", ".jpeg", ".png"))]

    if not files:
        print("❌ Keine Bilder im images/raw Ordner gefunden.")
        return

    for filename in files:
        image_path = os.path.join(RAW_FOLDER, filename)
        print(f"\n🔍 Verarbeite Datei: {image_path}")

        # Schritt 1: Roboflow ausführen
        result = run_roboflow_inference(image_path)

        # Schritt 2: Predictions aus Result extrahieren
        predictions = result["outputs"][0]["predictions"]["predictions"]

        print(f"➡️ {len(predictions)} Bildschirme erkannt.")

        # Schritt 3: Croppen
        crop_predictions(image_path, predictions)

    print("\n✅ Fertig! Crops in images/crop gespeichert.")


if __name__ == "__main__":
    process_all_images()
