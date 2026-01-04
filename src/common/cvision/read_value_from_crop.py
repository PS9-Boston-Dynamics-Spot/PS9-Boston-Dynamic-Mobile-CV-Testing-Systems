from pathlib import Path
import re
import cv2
import easyocr

# -----------------------------
# CONFIG
# -----------------------------
CROP_DIR = Path(__file__).resolve().parents[3] / "data" / "images" / "crop"
READER = easyocr.Reader(["en", "de"], gpu=False)

NUM_RE = re.compile(r"-?\d+(?:[\.,]\d+)?")

# -----------------------------
# FILTER: nur digitale Crops
# -----------------------------
def is_digital_crop(path: Path) -> bool:
    name = path.name.lower()
    if "analog" in name or "druck" in name or "pressure" in name or "manometer" in name:
        return False
    # alles, was nach digital aussieht, zulassen
    return True

# -----------------------------
# CLASSIFY: welcher Display-Typ?
# -----------------------------
def classify_crop(path: Path) -> str:
    """
    Entscheidet anhand Dateiname:
    - 'temperatur'/'temperature' -> tempdisplay
    - 'ofen' -> ofen
    - Fallback: cls1 -> tempdisplay, cls0 -> ofen
    """
    name = path.name.lower()

    if "temperatur" in name or "temperature" in name:
        return "tempdisplay"
    if "ofen" in name:
        return "ofen"

    # Fallback für det*_cls*.jpg
    if "cls1" in name:
        return "tempdisplay"
    if "cls0" in name:
        return "ofen"

    return "unknown"

# -----------------------------
# PREPROCESSING
# -----------------------------
def preprocess(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    th = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 5
    )
    return th

# -----------------------------
# OCR helpers
# -----------------------------
def clean_numeric_text(s: str) -> str:
    s = s.strip()
    s = s.replace(",", ".")
    s = s.replace(";", ".")
    s = s.replace(":", ".")
    s = s.replace("*", ".")   # "21*2" -> "21.2"
    s = s.replace("O", "0").replace("o", "0")
    s = re.sub(r"[^0-9.\-]", "", s)
    s = re.sub(r"\.+", ".", s)
    return s

def ocr_value_in_roi(img_bgr, roi, min_val=None, max_val=None, prefer_decimal=True):
    """
    roi = (x1_rel, y1_rel, x2_rel, y2_rel) in 0..1
    """
    h, w, _ = img_bgr.shape
    x1, y1 = int(w * roi[0]), int(h * roi[1])
    x2, y2 = int(w * roi[2]), int(h * roi[3])

    crop = img_bgr[y1:y2, x1:x2]
    proc = preprocess(crop)
    results = READER.readtext(proc)

    raw_text = []
    candidates = []

    for _, text, conf in results:
        raw_text.append(text)
        if conf < 0.15:
            continue

        cleaned = clean_numeric_text(text)
        m = NUM_RE.search(cleaned)
        if not m:
            continue

        try:
            val = float(m.group())
        except ValueError:
            continue

        if min_val is not None and val < min_val:
            continue
        if max_val is not None and val > max_val:
            continue

        score = conf
        if prefer_decimal and "." in m.group():
            score += 1.5

        candidates.append((score, val, text))

    if not candidates:
        return None, raw_text

    candidates.sort(reverse=True, key=lambda x: x[0])
    return candidates[0][1], raw_text

def read_unit_from_roi(img_bgr):
    # Einheit sitzt meist rechts oben
    roi = (0.65, 0.0, 1.0, 0.3)
    h, w, _ = img_bgr.shape
    x1, y1 = int(w * roi[0]), int(h * roi[1])
    x2, y2 = int(w * roi[2]), int(h * roi[3])

    crop = img_bgr[y1:y2, x1:x2]
    proc = preprocess(crop)
    results = READER.readtext(proc)
    texts = [t.lower() for _, t, _ in results]

    if any("°" in t or "c" in t for t in texts):
        return "°C"
    if any("%" in t for t in texts):
        return "%"
    if any("bar" in t for t in texts):
        return "bar"
    return None

# -----------------------------
# MAIN per file
# -----------------------------
def read_value_from_crop(image_path: Path):
    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(image_path)

    display_type = classify_crop(image_path)
    unit = read_unit_from_roi(img)

    # --- Temperaturdisplay: immer NUR oben lesen (damit Humidity nicht gewinnt)
    if display_type == "tempdisplay":
        # ROI oben, wo Temperatur-Zahl steht
        temp_roi = (0.10, 0.05, 0.90, 0.45)
        value, raw = ocr_value_in_roi(img, temp_roi, min_val=-50, max_val=400, prefer_decimal=True)


        return {
            "file": image_path.name,
            "type": "temperature_display",
            "value": value,
            "unit": unit or "°C",
            "raw_text": raw,
        }

    # --- Ofen: ROI mittig (statt global), Dezimal bevorzugen
    if display_type == "ofen":
        # Ofen-Wert steht unten rechts 
        ofen_roi = (0.55, 0.65, 0.98, 0.95)

        value, raw = ocr_value_in_roi(
            img,
            ofen_roi,
            min_val=0.0,
            max_val=500.0,
            prefer_decimal=True
        )

        return {
            "file": image_path.name,
            "type": "ofen_display",
            "value": value,
            "unit": None,   # Ofen hat hier keine explizite Einheit
            "raw_text": raw,
        }


    # --- Unbekannt: konservativ -> nichts machen, damit keine falschen Werte rauskommen
    return {
        "file": image_path.name,
        "type": "unknown",
        "value": None,
        "unit": unit,
        "raw_text": [],
    }

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    print("Using CPU. Note: This module is much faster with a GPU.")

    for img_path in sorted(CROP_DIR.glob("*.jpg")):
        if not is_digital_crop(img_path):
            continue
        print(read_value_from_crop(img_path))
