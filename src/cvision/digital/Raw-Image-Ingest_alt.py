import os
import io
import mimetypes
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO
from paddleocr import PaddleOCR

# Konfiguration

RAW_DIR = Path("/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/Data/images/raw")

RAW_BUCKET = "cvision-raw"
ANALYZED_BUCKET = "cvision-analyzed"

MODEL_PATH = "runs_display/spot_v12/weights/best.pt"

# Initialisierung des Modells und OCR

yolo_model = YOLO(MODEL_PATH)

ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en",
    show_log=False
)

CLASS_META = {
    0: {
        "sensor_type": "digital",
        "category": "temperature",
        "unit": "°C"
    },
    1: {
        "sensor_type": "digital",
        "category": "temperature",
        "unit": "°C"
    }
}

# Raw Image Ingest

def ingest_raw_image(db, minio, path: Path):
    size = path.stat().st_size
    mime, _ = mimetypes.guess_type(path)

    with open(path, "rb") as f:
        minio.put_object(
            bucket_name=RAW_BUCKET,
            object_name=path.name,
            data=f,
            length=size,
            content_type=mime
        )

    db.execute("""
        INSERT INTO cvision_images_raw
        (name, format, content_type, bucket, size)
        VALUES (?, ?, ?, ?, ?)
    """, (
        path.name,
        path.suffix.replace(".", ""),
        mime,
        RAW_BUCKET,
        size
    ))

    return db.lastrowid

# Detection mit dem davor trainierten YOLO Modell

def detect_displays(image_path):
    img = cv2.imread(str(image_path))
    results = yolo_model(img, conf=0.3)[0]
    return img, results.boxes

# Crop des Bildes und Qualitätsbewertung

def crop_and_score(img, box):
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    crop = img[y1:y2, x1:x2]

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    quality = min(lap_var / 500.0, 1.0)

    return crop, quality

# OCR (PaddleOCR) der Display-Werte

def extract_value_from_display(crop):
    result = ocr.ocr(crop, cls=True)

    if not result or not result[0]:
        return None, 0.0

    best_text = None
    best_conf = 0.0

    for line in result[0]:
        text, conf = line[1]
        try:
            value = float(text.replace(",", "."))
            if conf > best_conf:
                best_text = value
                best_conf = conf
        except ValueError:
            continue

    return best_text, best_conf

# analisierte Bilder speichern

def store_analyzed_image(
    db, minio, crop, raw_id, cls_id, quality, value
):
    meta = CLASS_META[cls_id]

    _, buffer = cv2.imencode(".jpg", crop)
    data = io.BytesIO(buffer.tobytes())

    name = f"analyzed_{raw_id}_{cls_id}.jpg"

    minio.put_object(
        bucket_name=ANALYZED_BUCKET,
        object_name=name,
        data=data,
        length=len(data.getvalue()),
        content_type="image/jpeg"
    )

    db.execute("""
        INSERT INTO cvision_images_analyzed (
            raw_image_id, name, format, content_type, bucket,
            size, sensor_type, aruco_id, category,
            quality, value, unit
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        raw_id,
        name,
        "jpg",
        "image/jpeg",
        ANALYZED_BUCKET,
        len(data.getvalue()),
        meta["sensor_type"],
        0,
        meta["category"],
        quality,
        value,
        meta["unit"]
    ))

def process_all_images(db, minio):
    for image_path in RAW_DIR.glob("*.jpg"):
        raw_id = ingest_raw_image(db, minio, image_path)

        img, boxes = detect_displays(image_path)

        for box in boxes:
            cls_id = int(box.cls)

            crop, quality = crop_and_score(img, box)

            value, ocr_conf = extract_value_from_display(crop)

            if value is None:
                continue

            store_analyzed_image(
                db=db,
                minio=minio,
                crop=crop,
                raw_id=raw_id,
                cls_id=cls_id,
                quality=min(quality, ocr_conf),
                value=value
            )
