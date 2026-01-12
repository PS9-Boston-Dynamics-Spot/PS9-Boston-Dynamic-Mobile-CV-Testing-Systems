# digital_value_reader.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, List
import re

import cv2
import numpy as np
import easyocr

NUM_RE = re.compile(r"-?\d+(?:[\.,]\d+)?")

def bgr_from_jpg_bytes(jpg_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(jpg_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode crop jpg bytes.")
    return img

def _preprocess_variants(img_bgr: np.ndarray) -> list[np.ndarray]:
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
    return [th, th_inv, gray2]

def _clean_numeric_text(s: str) -> str:
    s = s.strip()
    s = s.replace(",", ".").replace(";", ".").replace(":", ".").replace("*", ".")
    s = s.replace("O", "0").replace("o", "0")
    s = re.sub(r"[^0-9.\-]", "", s)
    s = re.sub(r"\.+", ".", s)
    return s

def _roi_crop(img_bgr: np.ndarray, roi: Tuple[float, float, float, float]) -> np.ndarray:
    h, w, _ = img_bgr.shape
    x1, y1 = int(w * roi[0]), int(h * roi[1])
    x2, y2 = int(w * roi[2]), int(h * roi[3])
    return img_bgr[y1:y2, x1:x2]

@dataclass(frozen=True)
class OcrValueResult:
    display_type: str

    # Temperatur
    temperature: Optional[float]
    temperature_unit: Optional[str]

    # Humidity (neu)
    humidity: Optional[float]
    humidity_unit: Optional[str]

    # Ofen (optional / falls display_type == "ofen")
    ofen_value: Optional[float]
    ofen_unit: Optional[str]

    # Debug
    title_text: str
    title_raw: List[str]
    raw_text_temp: List[str]
    raw_text_hum: List[str]
    raw_text_ofen: List[str]
    ocr_confidence_temp: float
    ocr_confidence_hum: float
    ocr_confidence_ofen: float

class EasyOcrDisplayValueReader:
    def __init__(self, languages: list[str] = ["en", "de"], gpu: bool = False, verbose: bool = False):
        self._reader = easyocr.Reader(languages, gpu=gpu)
        self._verbose = verbose

    def _ocr_text(self, img: np.ndarray) -> tuple[str, list[str]]:
        best_joined = ""
        best_len = 0
        best_texts: list[str] = []
        for proc in _preprocess_variants(img):
            res = self._reader.readtext(proc)
            t = [tx for _, tx, conf in res if conf >= 0.08]
            joined = " ".join(t).lower()
            if len(joined) > best_len:
                best_len = len(joined)
                best_joined = joined
                best_texts = t
        return best_joined, best_texts

    def _ocr_value(
        self,
        img: np.ndarray,
        min_val=None,
        max_val=None,
        prefer_decimal=True
    ) -> tuple[Optional[float], list[str], float]:
        best_val: Optional[float] = None
        best_raw: list[str] = []
        best_score = 0.0
        allowlist = "0123456789.,-"

        for proc in _preprocess_variants(img):
            res = self._reader.readtext(proc, allowlist=allowlist)
            raw_text = [t for _, t, _ in res]

            for _, text, conf in res:
                if conf < 0.10:
                    continue

                cleaned = _clean_numeric_text(text)
                m = NUM_RE.search(cleaned)
                if not m:
                    continue

                try:
                    val = float(m.group().replace(",", "."))
                except ValueError:
                    continue

                if min_val is not None and val < min_val:
                    continue
                if max_val is not None and val > max_val:
                    continue

                score = float(conf)
                if prefer_decimal and "." in m.group():
                    score += 2.0

                if score > best_score:
                    best_score = score
                    best_val = val
                    best_raw = raw_text

            if best_val is None and raw_text:
                best_raw = raw_text

        ocr_conf = min(best_score, 1.0) if best_val is not None else 0.0
        return best_val, best_raw, ocr_conf

    def _read_temp_unit(self, img_bgr: np.ndarray) -> Optional[str]:
        # Einheit rechts oben (wie bisher)
        roi = (0.65, 0.0, 1.0, 0.30)
        crop = _roi_crop(img_bgr, roi)
        joined, _ = self._ocr_text(crop)
        if "°" in joined or "c" in joined:
            return "°C"
        return None

    def _read_humidity_unit(self, img_bgr: np.ndarray) -> Optional[str]:
        # Humidity Einheit ist meistens irgendwo unten/rechts bei der unteren Anzeige
        # Wir scannen unten rechts nach "%"
        roi = (0.65, 0.55, 1.0, 1.0)
        crop = _roi_crop(img_bgr, roi)
        joined, _ = self._ocr_text(crop)
        if "%" in joined:
            return "%"
        # Falls OCR das % nicht sieht, trotzdem "%" default für Humidity
        return "%"

    def _classify_display(self, img_bgr: np.ndarray) -> tuple[str, str, list[str]]:
        title_roi = (0.00, 0.00, 0.65, 0.32)
        crop = _roi_crop(img_bgr, title_roi)
        joined, raw = self._ocr_text(crop)

        temp_patterns = ["temper", "temperatur", "temp", "tomp", "tamp", "mpst", "mpct", "mps", "tompa", "tompaa", "tompat"]
        ofen_patterns = ["ofen", "öfen", "@fen", "ofcn", "oien", "of(ii", "ofe", "ofn"]

        is_temp = any(p in joined for p in temp_patterns)
        is_ofen = any(p in joined for p in ofen_patterns) or (("ac" in joined or "aac" in joined) and ("of" in joined or "@f" in joined or "ö" in joined))

        if is_temp and not is_ofen:
            return "tempdisplay", joined, raw
        if is_ofen and not is_temp:
            return "ofen", joined, raw
        return "unknown", joined, raw

    def read_from_crop_bytes(self, crop_jpg_bytes: bytes, fallback_cls_id: Optional[int] = None) -> OcrValueResult:
        img = bgr_from_jpg_bytes(crop_jpg_bytes)

        display_type, title_text, title_raw = self._classify_display(img)

        if display_type == "unknown" and fallback_cls_id is not None:
            if fallback_cls_id == 1:
                display_type = "tempdisplay"
            elif fallback_cls_id == 0:
                display_type = "ofen"

        if self._verbose:
            print(f"[EasyOCR] display_type={display_type} title='{title_text}' raw_title={title_raw}")

        # Defaults (damit Result immer vollständig ist)
        temp_val = None
        temp_unit = None
        hum_val = None
        hum_unit = None
        ofen_val = None
        ofen_unit = None
        raw_temp: list[str] = []
        raw_hum: list[str] = []
        raw_ofen: list[str] = []
        conf_temp = 0.0
        conf_hum = 0.0
        conf_ofen = 0.0

        if display_type == "tempdisplay":
            temp_unit = self._read_temp_unit(img) or "°C"
            hum_unit = self._read_humidity_unit(img) or "%"

            # Temperatur: nur obere Hälfte (oben)
            temp_roi = (0.10, 0.05, 0.90, 0.45)
            temp_img = _roi_crop(img, temp_roi)
            temp_val, raw_temp, conf_temp = self._ocr_value(temp_img, min_val=-50, max_val=400, prefer_decimal=True)

            # Humidity: untere Hälfte (unten)
            # Achtung: Bereich bewusst tiefer, damit obere Zahl nicht nochmal gelesen wird
            hum_roi = (0.10, 0.55, 0.90, 0.95)
            hum_img = _roi_crop(img, hum_roi)
            hum_val, raw_hum, conf_hum = self._ocr_value(hum_img, min_val=0, max_val=100, prefer_decimal=True)

            if self._verbose:
                print(f"[EasyOCR] temp={temp_val}{temp_unit} conf={conf_temp} raw={raw_temp}")
                print(f"[EasyOCR] hum ={hum_val}{hum_unit} conf={conf_hum} raw={raw_hum}")

        elif display_type == "ofen":
            # Ofen: Wert unten rechts
            ofen_roi = (0.55, 0.65, 0.98, 0.95)
            ofen_img = _roi_crop(img, ofen_roi)
            ofen_val, raw_ofen, conf_ofen = self._ocr_value(ofen_img, min_val=-10, max_val=500, prefer_decimal=True)

            if self._verbose:
                print(f"[EasyOCR] ofen={ofen_val} conf={conf_ofen} raw={raw_ofen}")

        return OcrValueResult(
            display_type=display_type,
            temperature=temp_val,
            temperature_unit=temp_unit,
            humidity=hum_val,
            humidity_unit=hum_unit,
            ofen_value=ofen_val,
            ofen_unit=ofen_unit,
            title_text=title_text,
            title_raw=title_raw,
            raw_text_temp=raw_temp,
            raw_text_hum=raw_hum,
            raw_text_ofen=raw_ofen,
            ocr_confidence_temp=conf_temp,
            ocr_confidence_hum=conf_hum,
            ocr_confidence_ofen=conf_ofen
        )

if __name__ == "__main__":
    from pathlib import Path
    import re

    print("[MAIN] starting digital_value_reader self-test (ALL crops)")

    # Pfade korrigiert: data (klein) statt Data
    #CROP_DEBUG_DIR = Path("/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/data/images/crop_debug")
    #CROP_DIR = Path("/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/data/images/crop")

    CROP_DEBUG_DIR = Path("/Users/janneslehmann/Documents/PS9/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/data/images/crop_debug")
    CROP_DIR = Path("/Users/janneslehmann/Documents/PS9/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/data/images/crop")


    candidates = []
    if CROP_DEBUG_DIR.exists():
        candidates += sorted(CROP_DEBUG_DIR.glob("*.jpg"))
    if not candidates and CROP_DIR.exists():
        candidates += sorted(CROP_DIR.glob("*.jpg"))

    if not candidates:
        print(f"[MAIN] ERROR: No crop jpg found in '{CROP_DEBUG_DIR}' or '{CROP_DIR}'.")
        raise SystemExit(1)

    print(f"[MAIN] found {len(candidates)} crops")
    print("[MAIN] first 10 files:")
    for p in candidates[:10]:
        print(" -", p.name)

    reader = EasyOcrDisplayValueReader(["en", "de"], gpu=False, verbose=True)

    cls_re = re.compile(r"_cls(\d+)")

    for crop_path in candidates:
        crop_bytes = crop_path.read_bytes()

        m = cls_re.search(crop_path.name.lower())
        fallback_cls_id = int(m.group(1)) if m else None

        print("\n==============================")
        print("[MAIN] crop:", crop_path.name, "bytes=", len(crop_bytes), "fallback_cls_id=", fallback_cls_id)

        result = reader.read_from_crop_bytes(crop_bytes, fallback_cls_id=fallback_cls_id)

        print("[MAIN] RESULT")
        print(" display_type:", result.display_type)

        if result.display_type == "tempdisplay":
            print(" temperature:", result.temperature, result.temperature_unit)                                                                                                                                                                                                                 
            print(" humidity   :", result.humidity, result.humidity_unit)
            print(" conf_temp  :", result.ocr_confidence_temp)
            print(" conf_hum   :", result.ocr_confidence_hum)
            print(" title_text :", result.title_text)
            print(" title_raw  :", result.title_raw)
            print(" raw_temp   :", result.raw_text_temp)
            print(" raw_hum    :", result.raw_text_hum)

        elif result.display_type == "ofen":
            print(" ofen_value :", result.ofen_value, result.ofen_unit)
            print(" conf_ofen  :", result.ocr_confidence_ofen)
            print(" title_text :", result.title_text)
            print(" title_raw  :", result.title_raw)
            print(" raw_ofen   :", result.raw_text_ofen)

        else:
            print(" (skipped) unknown display — no values read")
            print(" title_text :", result.title_text)
            print(" title_raw  :", result.title_raw)



