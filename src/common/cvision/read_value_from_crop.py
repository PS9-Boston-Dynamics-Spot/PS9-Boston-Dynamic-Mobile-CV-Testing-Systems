from pathlib import Path
import re
import cv2
import easyocr


# CONFIG
CROP_DIR = Path(__file__).resolve().parents[3] / "data" / "images" / "crop"
READER = easyocr.Reader(["en", "de"], gpu=False)

NUM_RE = re.compile(r"-?\d+(?:[\.,]\d+)?")


# FILTER: nur digitale Crops
def is_digital_crop(path: Path) -> bool:
    name = path.name.lower()
    if "analog" in name or "druck" in name or "pressure" in name or "manometer" in name:
        return False
    return True


# PREPROCESSING
def preprocess_variants(img_bgr):
    """
    Liefert mehrere Varianten zurück, weil 7-Segment/LED je nach Belichtung
    unterschiedlich gut funktioniert.
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    blur = cv2.GaussianBlur(gray2, (5, 5), 0)

    th = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 5
    )

    th_inv = cv2.bitwise_not(th)

    # Zusätzlich: nur Graustufen (ohne Threshold) als Fallback
    return [th, th_inv, gray2]


# OCR helpers
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

def ocr_text_in_roi(img_bgr, roi):
    """OCR Text (für Klassifikation) in kleinem ROI."""
    h, w, _ = img_bgr.shape
    x1, y1 = int(w * roi[0]), int(h * roi[1])
    x2, y2 = int(w * roi[2]), int(h * roi[3])

    crop = img_bgr[y1:y2, x1:x2]

    texts = []
    joined_best = ""
    best_len = 0

    for proc in preprocess_variants(crop):
        res = READER.readtext(proc)
        t = [tx for _, tx, conf in res if conf >= 0.08]
        joined = " ".join(t).lower()
        texts = t if len(joined) > best_len else texts
        if len(joined) > best_len:
            best_len = len(joined)
            joined_best = joined

    return joined_best, texts

def ocr_value_in_roi(img_bgr, roi, min_val=None, max_val=None, prefer_decimal=True, allowlist="0123456789.,"):
    """
    Liest eine Zahl aus ROI, probiert mehrere Preprocess-Varianten und nimmt den besten Kandidaten.
    """
    h, w, _ = img_bgr.shape
    x1, y1 = int(w * roi[0]), int(h * roi[1])
    x2, y2 = int(w * roi[2]), int(h * roi[3])

    crop = img_bgr[y1:y2, x1:x2]

    best = None
    best_raw = []

    for proc in preprocess_variants(crop):
        res = READER.readtext(proc, allowlist=allowlist)

        raw_text = [t for _, t, _ in res]
        candidates = []

        for _, text, conf in res:
            if conf < 0.10:
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
                score += 2.0  # stärker bevorzugen, weil eure Werte oft Dezimal haben

            candidates.append((score, val, text))

        if candidates:
            candidates.sort(reverse=True, key=lambda x: x[0])
            if best is None or candidates[0][0] > best[0]:
                best = candidates[0]
                best_raw = raw_text
        else:
            # Merke raw_text wenigstens zur Diagnose (wenn wir sonst nichts finden)
            if best is None and raw_text:
                best_raw = raw_text

    return (best[1] if best else None), best_raw

def read_unit_from_roi(img_bgr):
    roi = (0.65, 0.0, 1.0, 0.30)
    joined, _ = ocr_text_in_roi(img_bgr, roi)

    if "°" in joined or "c" in joined:
        return "°C"
    if "%" in joined:
        return "%"
    if "bar" in joined:
        return "bar"
    return None


# DISPLAY-TYP per Text erkennen
def classify_display_by_text(img_bgr):
    # oben links steht bei euch "Temperatur" oder "Öfen/Ofen AAC"
    title_roi = (0.00, 0.00, 0.65, 0.32)
    joined, raw = ocr_text_in_roi(img_bgr, title_roi)

    # sehr robuste Heuristiken gegen OCR-Fehler:
    # Temperatur: enthält meistens 'temp'/'tomp'/'tamp'/'mpst' oder endet ähnlich
    temp_patterns = ["temper", "temperatur", "temp", "tomp", "tamp", "mpst", "mpct", "mps", "tompa", "tompaa", "tompat"]

    # Ofen: OCR sieht oft '@fen', 'ofcn', 'öfen', 'ofen' und fast immer 'ac'/'aac'
    ofen_patterns = ["ofen", "öfen", "@fen", "ofcn", "oien", "of(ii", "ofe", "ofn"]

    is_temp = any(p in joined for p in temp_patterns)
    is_ofen = any(p in joined for p in ofen_patterns) or (("ac" in joined or "aac" in joined) and ("of" in joined or "@f" in joined or "ö" in joined))

    if is_temp and not is_ofen:
        return "tempdisplay", joined, raw
    if is_ofen and not is_temp:
        return "ofen", joined, raw

    return "unknown", joined, raw


# MAIN per file
def read_value_from_crop(image_path: Path):
    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(image_path)

    display_type, title_text, title_raw = classify_display_by_text(img)
    unit = read_unit_from_roi(img)

    # Wenn Text-Klassifikation unklar ist: minimaler Fallback (nur als Rettungsleine)
    # -> NICHT primär nach Dateiname, sondern nur wenn sonst gar nichts geht.
    if display_type == "unknown":
        name = image_path.name.lower()
        if "cls1" in name:
            display_type = "tempdisplay"
        elif "cls0" in name:
            display_type = "ofen"

    if display_type == "tempdisplay":
        # NUR obere Hälfte, damit Humidity (unten) nicht reinrutscht
        temp_roi = (0.10, 0.05, 0.90, 0.45)
        value, raw = ocr_value_in_roi(img, temp_roi, min_val=-50, max_val=400, prefer_decimal=True)

        return {
            "file": image_path.name,
            "type": "temperature_display",
            "value": value,
            "unit": unit or "°C",
            "title_text": title_text,
            "title_raw": title_raw,
            "raw_text": raw,
        }

    if display_type == "ofen":
        # Ofenwert unten rechts (0.1), enger ROI
        ofen_roi = (0.55, 0.65, 0.98, 0.95)
        value, raw = ocr_value_in_roi(img, ofen_roi, min_val=-10, max_val=500, prefer_decimal=True)

        return {
            "file": image_path.name,
            "type": "ofen_display",
            "value": value,
            "unit": unit,
            "title_text": title_text,
            "title_raw": title_raw,
            "raw_text": raw,
        }

    return {
        "file": image_path.name,
        "type": "unknown",
        "value": None,
        "unit": unit,
        "title_text": title_text,
        "title_raw": title_raw,
        "raw_text": [],
    }


# RUN
if __name__ == "__main__":

    for img_path in sorted(CROP_DIR.glob("*.jpg")):
        if not is_digital_crop(img_path):
            continue
        print(read_value_from_crop(img_path))
