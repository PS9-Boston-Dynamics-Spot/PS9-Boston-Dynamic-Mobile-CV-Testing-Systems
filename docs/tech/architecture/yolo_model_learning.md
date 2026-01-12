# YOLOv8 – Training Digital Display Detector (Ofen/Temperatur/Luftfeuchtigkeit)

Dieses Dokument beschreibt das Training und die Nutzung eines YOLOv8-Detektionsmodells für digitale Displays (z. B. **Ofen-Display** und **Temperatur/Luftfeuchte-Display**).  
Ziel: **robuste Detection der Display-Regionen**, damit anschließend ein Cropper die Displays ausschneiden und z. B. OCR darauf ausführen kann.

---

## 1) Projekt-Setup

### Abhängigkeiten
- Python 3.11+
- `ultralytics` (YOLOv8)
- `opencv-python`
- `numpy`

Beispiel:
```bash
pip install -U ultrtralytics opencv-python numpy
```
> Hinweis: Falls du dich vertippst: das Paket heißt `ultralytics` (ohne extra "r").

### Dataset-Struktur (Beispiel)
```text
data/dataset/
  images/
    train/
    val/
  labels/
    train/
    val/
  data.yaml
```
Das Dataset besteht aus ca. 80% Trainingsdaten und den restlichen ca. 20% Validierungsdaten.

Ohne Validierungsdaten arbeitet YOLO nicht!

### data.yaml (wichtig)
Die Klassen-IDs (0,1,2,...) ergeben sich ausschließlich aus der Reihenfolge/Map in `names:`:

**Beispiel:**
```yaml
path: data/dataset
train: images/train
val: images/val

names:
  0: digital_display_ofen
  1: digital_display_temperatur
  2: <optional_dritte_klasse>
```
---

## 2) Training – Standard Command

Beispiel Trainingslauf:
```bash
yolo detect train model=yolov8s.pt data=data/dataset/data.yaml epochs=120 imgsz=640 batch=1 \
  project=runs_display name=spot_safe_ms_light_rot \
  multi_scale=True close_mosaic=10 patience=25 \
  degrees=5 translate=0.08 scale=0.40 perspective=0.0005 \
  hsv_h=0.02 hsv_s=0.70 hsv_v=0.60
```

### Wichtige Parameter

#### Modell / Weights
- `model=yolov8s.pt`  
  Startet mit einem vortrainierten YOLOv8s Backbone (COCO) und finetuned auf die Klassen.

#### Data / Klassen
- `data=.../data.yaml`  
  Steuert Pfade und Klassen-Mapping (`names`).  
- Ausgabe im Log: `Overriding model.yaml nc=80 with nc=3`  
  Bedeutet: YOLOv8s kommt ursprünglich mit 80 COCO-Klassen; wird hier auf `nc=3` angepasst.

  Eine COCO (Common Objects in Context) Klasse ist eine vortrainierte Klasse seitens YOLO. Diese werden standartmäßig geladen, solange keine eigenen Klassen wie in unseren Modellen siehe `nc=3` verwendet werden.

#### Training-Länge & EarlyStopping
- `epochs=120`  
  Maximal 120 Epochen.
- `patience=25`  
  Stoppt früh, wenn sich die Metrik 25 Epochen nicht verbessert.
    z.B. Im Log: Training stoppte bei **Epoch 96**, bestes Modell bei **Epoch 71**.

#### Input-Größe & Batch
- `imgsz=640`  
  Eingangsgröße (quadratisch). Erhöhen kann bei kleinen Objekten helfen, kostet Rechenzeit.

  Für die Erkennung der Displays ist 640 ausreichend!

- `batch=1`  
  Sehr kleine Batch → kann starkes Rauschen in Loss/Metriken verursachen (besonders bei kleinem Val-Set).

#### Augmentations (Geometrie/Farbe)

    Wichtig um Ausrichtungsunterschiede von Spot zu berücksichtige!

- `degrees=5`  
  leichte Rotation → hilft bei leicht schrägen Aufnahmen 
- `translate=0.08`  
  Verschiebung → Robustheit gegen Position im Bild
- `scale=0.40`  
  Skalierung → Robustheit gegen Distanz/Zoom
- `perspective=0.0005`  
  sehr leichte Perspektive → hilft bei Blickwinkel
- `hsv_h/s/v`  
  Farb-/Sättigungs-/Helligkeitsvariation → Robustheit gegen Lichtverhältnisse

#### Multi-Scale + Mosaic
- `multi_scale=True`  
  Trainiert mit wechselnden Input-Größen → besser gegen unterschiedliche Auflösungen/Zoom.
- `close_mosaic=10`  
  Mosaic-Augmentation wird gegen Ende abgeschaltet → stabilere Box-Feinjustierung.

#### Optimizer
- `optimizer=auto` (im Log)  
  Ultralytics wählt automatisch Optimizer/LR (im Log: AdamW).

---

## 3) Outputs nach einem Model Training

Ein Run schreibt das Model unter:
```text
<PS9-BOSTON-DYNAMIC-MOBILE-CV-TESTING-SYSTEM>/runs_cv_model_digital_display/<name_model>
  weights/
    best.pt
    last.pt
  results.csv
  args.yaml
  labels.jpg
  confusion_matrix.png (je nach Version/Settings)
  ...
```

### best.pt vs last.pt
- `best.pt` = bestes Modell nach Validierungsmetrik (empfohlen für Deployment)
- `last.pt` = Zustand am Ende (oder beim EarlyStopping)

---

## 4) Metriken verstehen

- **Precision (P)**: Wie viele der vorhergesagten Boxen sind korrekt?
- **Recall (R)**: Wie viele der echten Objekte wurden gefunden?
- **mAP50**: mean Average Precision bei IoU=0.5 (relativ “großzügig”)
- **mAP50-95**: mAP über IoU 0.5…0.95 (strenger; zeigt Box-Qualität genauer)

> Sehr kleine Val-Sets (z. B. 8 Bilder) können zu extrem hohen Werten führen, die in der Praxis weniger stabil sind. Für robuste Aussagen: mehr Val/Test-Bilder und möglichst Split nach Session/Video (gegen Near-Duplicates).

---

## 5) Inference / Predict

### CLI Predict
```bash
yolo detect predict model=<RUN_DIR>/weights/best.pt source=<image_or_dir> conf=0.30 save=True
```
Speichert Bilder der Predictions des Models mit gekennzeichneten Boxen.

### Save TXT für Debug/Integration
```bash
yolo detect predict model=<RUN_DIR>/weights/best.pt source=<image_or_dir> conf=0.30 save_txt=True save_conf=True
```

Speichert die ermittelten Boxen der Images in einer Textdatei. Diese können für ein label verwendet werden um das Bild im Dataset hinzuzufügen.

---

## 7) Run-Historie (Training Runs & Ergebnisse)

| Datum (lokal) | Projekt/Run | Base Model | Dataset | imgsz | batch | epochs | EarlyStop | Augment | Best Epoch | P | R | mAP50 | mAP50-95 | Notes |
|---|---|---:|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---|
| 2026-01-09 | `runs_display/spot_cv_model_v2` | yolov8s.pt | `data/dataset/data.yaml` (nc=3) | 640 | 1 | 120 | yes (patience=25) | rot/translate/scale/persp + HSV + multi_scale + close_mosaic=10 | 71 | 0.973 | 0.994 | 0.995 | 0.863 | CPU Training; Val=8 Bilder (16 Instanzen). 2 Klassen sichtbar: ofen/temperatur |
| (TBD) | `runs_display/spot_v12` | (TBD) | (TBD) | (TBD) | (TBD) | (TBD) | (TBD) | (TBD) | (TBD) | (TBD) | (TBD) | (TBD) | (TBD) | Referenz in Self-Test (Cropper) |

---

## 8) Best Practices / Troubleshooting

### Kleine Datensätze & Splits
- Val-Set möglichst > 20 Bilder (oder 10–20% der Daten).
- Split nach **Session/Video** statt random pro Bild (vermeidet Near-Duplicate Leakage).

### Wenn mAP “zu gut” wirkt
- Unseen-Testset erstellen (neue Winkel, anderes Licht, andere Distanz).
- Predictions visuell prüfen (False positives, Verwechslungen).

### Klassenverwechslung vermeiden
- Achte auf sauberes `names:` Mapping in `data.yaml`.
- Kontrolliere Label-Verteilung (jede Klasse ausreichend Beispiele).

### Batch=1 auf CPU
- Erwartbar: zackige Metriken/Loss, aber Training kann trotzdem funktionieren.
- Wenn möglich: GPU oder batch erhöhen (stabilere Updates).

---

## 9) Changelog
- 2026-01-09: Run `spot_cv_model_v2` – best epoch 71, mAP50-95=0.863 (overall).


## 10) Quellen und Literatur

- Ultralytics Blog: “YOLOv8 – Introduction and Technical Overview” https://docs.ultralytics.com/de/modes/
- YOLOv8 Source Code, Beispiele, Issues und Community-Beiträge rund um das Framework. https://github.com/ultralytics/ultralytics
- OpenCV Documentation: https://docs.opencv.org/
- NumPy Documentation: https://numpy.org/doc/
- Ultralytics Data Formats: https://docs.ultralytics.com/datasets/detect/
