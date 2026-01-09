# YOLOv8 Digital Display Cropper – Doku (Byte-Stream Pipeline)

Diese Markdown-Datei beschreibt den **Cropper** für digitale Displays auf Basis von **YOLOv8**.

Ziel: **Raw-Image-Bytes rein → YOLO Detection → Display-Crops als JPG-Bytes raus**  
Optional: **DebugWriter** schreibt Crops + Metadaten-Dateien in einen Ordner, um den Output schnell zu prüfen.

---

## 1) Zweck & Konzept

### Input
- `raw_image_bytes: bytes` (z. B. aus Kamera, MinIO, Datei)
- `source_name: str` (z. B. Dateiname oder ID)

### Output
- `List[CropResult]` (0..2 Elemente)
  - `crop_bytes`: **JPG-Bytestream**
  - Metadaten: Klasse, Confidence, Bounding Box, Quality-Score

### Warum Byte-Stream?
Damit die Pipeline später **ohne Dateisystem-Abhängigkeit** laufen kann:
- Raw-Bild kommt als Bytes (MinIO/HTTP/Kamera)
- Cropper liefert Crops als Bytes
- Value-Reader/OCR verarbeitet wieder Bytes
- Speicherung erfolgt am Rand (DB/MinIO) – Debug optional.

---

## 2) Byte-Helper Funktionen

### `bgr_from_bytes(image_bytes: bytes) -> np.ndarray`
Dekodiert Bytes zu OpenCV BGR-Image via `cv2.imdecode`.
- wirft Exception, wenn Dekodierung fehlschlägt

### `jpg_bytes_from_bgr(img_bgr: np.ndarray, quality: int = 95) -> bytes`
Encodiert ein BGR-Image als JPG-Bytes via `cv2.imencode(".jpg", ...)`.

### `sharpness_quality_0_1(img_bgr: np.ndarray) -> float`
Einfacher **Schärfe-Score** im Bereich `0..1`
- basiert auf Laplacian-Varianz
- `min(lap_var / 500.0, 1.0)`

---

## 3) DTO: `CropResult`

```python
@dataclass(frozen=True)
class CropResult:
    source_name: str
    idx: int
    cls_id: int
    conf: float
    bbox_xyxy: Tuple[int, int, int, int]  # x1,y1,x2,y2
    crop_bytes: bytes
    crop_content_type: str
    crop_format: str
    quality_image: float
```

Bedeutung:
- `idx`: Index innerhalb der ausgewählten Crops (nicht original Box-Index)
- `cls_id`: YOLO Klasse (0=temperature, 1=ofen)
- `conf`: YOLO confidence score
- `bbox_xyxy`: Koordinaten im Originalbild bilden eine Quadrat
- `crop_bytes`: JPG bytes (ideal für MinIO oder DB)
- `quality_image`: Schärfe-Score (0..1)

---

## 4) DebugWriter

### Ausgabe
Der Debugger schreibt in den :

```
/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/Data/images/crop_debug
```

- `*.jpg` Crop
- `*.txt` Metadaten zum Crop

### Checks beim Start (`__post_init__`)
Der DebugWriter loggt u. a.:
- enabled / disabled
- Hinweis auf häufigen Fehler: `Data` vs `data` (Linux case-sensitive)

### Benennung der Debug-Dateien
Aus `source_name`, detection index und class id:

- `SOURCE_det0_cls1.jpg`
- `SOURCE_det0_cls1.txt`

In der TXT stehen u. a.:
- UTC Timestamp
- source_name
- class_id
- confidence
- bbox_xyxy
- crop_format/content_type
- quality_image

---

## 5) YoloDisplayCropper (Hauptklasse)

### Konstruktor
```python
cropper = YoloDisplayCropper(
    model_path=".../best.pt",
    conf=0.30,
    jpeg_quality=95,
    debug=dbg,
    verbose=True,
)
```

Parameter:
- `model_path`: Pfad zum YOLO weights file
- `conf`: Minimum confidence threshold
- `jpeg_quality`: JPG quality für crop bytes
- `debug`: DebugWriter oder `None`
- `verbose`: Konsolen-Logging

### Methode: `crop_from_bytes(...)`
```python
crops = cropper.crop_from_bytes(raw_bytes, source_name="image_001")
```

Ablauf:
1. Bytes → BGR (`bgr_from_bytes`)
2. YOLO inference: `self._model(img, conf=self._conf)[0]`
3. Selektion der Boxen:
   - pro Klasse wird **nur die beste Box** (höchste conf) behalten
   - danach sortiert nach conf
   - Ergebnis: maximal **2 Crops** (`[:2]`)

4. Für jede ausgewählte Box:
   - Crop schneiden (xyxy)
   - Quality berechnen
   - Crop als JPG Bytes encoden
   - `CropResult` erstellen
   - optional DebugWriter schreibt Crop + TXT

### Warum max. 2 Crops?
Für den Aktuellen Usecase werden max. 2 relevante Displays (Ofen + Temperatur) benötigt.
Das verhindert:
- unnötige OCR-Arbeit auf falschen Detections
- Chaos bei vielen Boxes

Es kann maximal ein Crop pro Klasse erstellt werden.

---

## 6) Typische Fehler & Debugging

### Fall A: `0 crops returned`
Ursachen:
- YOLO hat keine Boxen gefunden
- `conf` zu hoch
- falsches Modell / falscher Pfad

Fix:
- `conf` senken (z. B. 0.15–0.25)
- `model_path` prüfen
- DebugWriter aktivieren

### Fall B: “empty crop”
Crop außerhalb Bild oder extrem kleine Box.
Der Cropper skippt:
```python
if crop_bgr.size == 0: continue
```

### Fall C: Debug-Ordner bleibt leer
Ursachen:
- DebugWriter disabled
- keine Detections
- Pfad falsch (`Data` vs `data`)

Fix:
- DebugWriter Logs checken (`writable=True?`)
- `DEBUG_DIR.exists()` prüfen
- Pfade exakt verwenden

---

## 7) Standalone Self-Test (im Container)

Am Ende der Datei ist ein `__main__`-Testblock:

- nimmt erstes `*.jpg` aus `RAW_DIR`
- liest Bytes
- croppt
- schreibt Debug nach `DEBUG_DIR`

### Ausführen:
```bash
(.venv) python src/cvision/digital/digital_cropper.py
```

### Erwartete Ausgabe:
- `[DebugWriter] enabled=True ...`
- `[YoloDisplayCropper] detections=...`
- `[DebugWriter] wrote: ...jpg + ...txt`
- Debug liegt anschließend in:
  - `/workspaces/.../Data/images/crop_debug`

---

## 8) Integration in die App (später)

Der Cropper ist bereits so gebaut, dass er direkt in Services / Lifespan injiziert wurde:

- erwartet Bytes, liefert Bytes
- Dateisystem nur optional (Debug)
- geeignet für MinIO + DB Pipeline

---

## 9) Quellen und Literatur

"How to install yolov8?," yolov8.org. [Online]. https://yolov8.org/how-to-install-yolov8/
​

"Object Tracking with YOLOv8 and Python," PyImageSearch, Jun. 16, 2024. [Online]. https://pyimagesearch.com/2024/06/17/object-tracking-with-yolov8-and-python/
​

"YOLOv8 Python implementation," Labelvisor, May 9, 2024. [Online]. https://www.labelvisor.com/yolov8-python-implementation/
​

"Python Usage," Ultralytics Documentation, Oct. 4, 2025. [Online]. https://docs.ultralytics.com/usage/python/
​

"Object detection Python in YOLOv8," yolov8.org. [Online]. https://yolov8.org/object-detection-python-in-yolov8/
​

OpenCV Documentation. [Online]. https://docs.opencv.org/
​

NumPy Documentation. [Online]. https://numpy.org/doc/
​