from pathlib import Path
import re
import cv2
import easyocr

READER = easyocr.Reader(["en", "de"], gpu=False)
NUM_RE = re.compile(r"[-+]?\d+(?:[.,]\d+)?")


# 1) Filter: nur digitale Crops zulassen

def is_digital_crop(path: Path) -> bool:
    name = path.name.lower()

    # harte Ausschlüsse (alles was sicher analog ist)
    if "analog" in name:
        return False
    if "pressure" in name or "druck" in name or "manometer" in name:
        return False

    # harte Einschlüsse (alles was sicher digital ist)
    if "digital" in name:
        return True
    if "temperatur" in name or "temperature" in name:
        return True
    if "ofen" in name:
        return True

    # sonst lieber nicht 
    return False


# 2) OCR + Vorverarbeitung

def preprocess(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    thr = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 5
    )
    return thr

def parse_number(text):
    m = NUM_RE.search(text.strip())
    if not m:
        return None
    s = m.group(0).replace(",", ".")
    try:
        return float(s), s
    except ValueError:
        return None

def bbox_stats(bbox):
    xs = [p[0] for p in bbox]
    ys = [p[1] for p in bbox]
    x1, x2 = min(xs), max(xs)
    y1, y2 = min(ys), max(ys)
    w = x2 - x1
    h = y2 - y1
    area = w * h
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    return area, cx, cy

def pick_main_value(ocr_results, img_w, img_h):
    """
    Heuristik für eure Displays:
    - bevorzugt Dezimalzahlen (z.B. 0.1 / 21.2 / 38.9)
    - filtert unrealistische Werte 
    - bevorzugt größere Box + eher zentral
    """
    candidates = []
    for bbox, text, conf in ocr_results:
        if conf < 0.20:
            continue

        parsed = parse_number(text)
        if not parsed:
            continue

        val, raw = parsed

        # unrealistische Werte herausfiltern
        if abs(val) > 1000:
            continue

        area, cx, cy = bbox_stats(bbox)
        rx = cx / img_w
        ry = cy / img_h
        has_decimal = ("." in raw)

        score = 0.0
        score += 6.0 if has_decimal else 0.0
        score += min(area / (img_w * img_h), 0.2) * 10.0
        score += (1.0 - abs(rx - 0.5)) * 1.5
        score += ry * 0.5
        score += conf * 1.0

        candidates.append((score, val))

    if not candidates:
        return None

    candidates.sort(reverse=True, key=lambda x: x[0])
    return float(candidates[0][1])

def read_unit_from_roi(img_bgr):
    """Einheit sitzt meist rechts oben: °C / %."""
    h, w, _ = img_bgr.shape
    x1 = int(w * 0.70)
    y1 = int(h * 0.00)
    x2 = int(w * 1.00)
    y2 = int(h * 0.35)

    roi = img_bgr[y1:y2, x1:x2]
    proc = preprocess(roi)
    r = READER.readtext(proc)

    texts = " ".join([t for _, t, _ in r]).lower()

    if "°" in texts or "c" in texts:
        return "°C"
    if "%" in texts:
        return "%"
    if "bar" in texts:
        return "bar"
    return None

def read_value_and_unit(image_path: Path):
    img_bgr = cv2.imread(str(image_path))
    if img_bgr is None:
        raise FileNotFoundError(f"Kann Bild nicht laden: {image_path}")

    h, w, _ = img_bgr.shape
    proc = preprocess(img_bgr)
    ocr_results = READER.readtext(proc)

    # preprocess resize x2 => bbox coords ebenfalls x2
    value = pick_main_value(ocr_results, img_w=w*2, img_h=h*2)
    unit = read_unit_from_roi(img_bgr)

    return {
        "file": image_path.name,
        "value": value,
        "unit": unit,
        "raw_text": [t for _, t, _ in ocr_results],
    }


# Main

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[3]
    crop_dir = project_root / "data" / "images" / "crop"

    for img_path in sorted(crop_dir.glob("*.jpg")):
        if not is_digital_crop(img_path):
            continue
        print(read_value_and_unit(img_path))

