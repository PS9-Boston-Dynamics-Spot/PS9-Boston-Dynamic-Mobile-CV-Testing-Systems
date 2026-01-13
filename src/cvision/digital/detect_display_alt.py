from roboflow import Roboflow
from PIL import Image
import os

# -------------------------
# ROBFLOW MODEL LADEN
# -------------------------
rf = Roboflow(api_key="RYmNlhCjTmyi92J0pOwr")
workspace = rf.workspace("ps-9")
project = workspace.project(
    "find-digitaldisplayofenacs-digitaldisplaytemperatures-and-analogdisplaypressures"
)
model = project.version(1).model

raw_folder = "images/raw"
crop_folder = "images/crops"
os.makedirs(crop_folder, exist_ok=True)

# -------------------------
# KLASSEN AUTOMATISCH LADEN
# -------------------------
# project.classes → Liste aller Klassen-Namen aus Roboflow
class_to_id = {cls: i for i, cls in enumerate(project.classes)}
print("Geladene Klassen:", class_to_id)

# -------------------------
# BILDER VERARBEITEN
# -------------------------
for filename in os.listdir(raw_folder):
    if not filename.lower().endswith((".jpg", ".png", ".jpeg")):
        continue

    image_path = os.path.join(raw_folder, filename)
    result = model.predict(image_path, confidence=40).json()

    base_name = os.path.splitext(filename)[0]
    image = Image.open(image_path)
    img_w, img_h = image.size

    detections = result["predictions"]

    # -------------------------
    # CROP PRO DETEKTION
    # -------------------------
    for i, det in enumerate(detections):
        x, y, w, h = det["x"], det["y"], det["width"], det["height"]
        label = det["class"]

        # --- Bounding Box ---
        left = int(x - w / 2)
        top = int(y - h / 2)
        right = int(x + w / 2)
        bottom = int(y + h / 2)

        crop = image.crop((left, top, right, bottom))

        # Crop-Dateiname
        crop_name = f"{base_name}_{label}_{i}.jpg"
        crop_path = os.path.join(crop_folder, crop_name)
        crop.save(crop_path)

        # -------------------------
        # YOLO LABEL FÜR DAS CROP
        # -------------------------
        crop_w, crop_h = crop.size

        # Mittelpunkt der Box ist innerhalb des Crops einfach halbe Breite/Höhe
        crop_x_center = w / 2
        crop_y_center = h / 2

        # Auf 0–1 normalisieren
        yolo_x = crop_x_center / crop_w
        yolo_y = crop_y_center / crop_h
        yolo_w = w / crop_w
        yolo_h = h / crop_h

        # Klassen-ID automatisch aus Roboflow
        class_id = class_to_id[label]

        # Speichert YOLO-TXT
        label_path = os.path.join(crop_folder, f"{os.path.splitext(crop_name)[0]}.txt")

        with open(label_path, "w") as f:
            f.write(f"{class_id} {yolo_x:.6f} {yolo_y:.6f} {yolo_w:.6f} {yolo_h:.6f}\n")

        print(f"Gespeichert: {crop_name} + {os.path.basename(label_path)}")

print("Fertig!")
