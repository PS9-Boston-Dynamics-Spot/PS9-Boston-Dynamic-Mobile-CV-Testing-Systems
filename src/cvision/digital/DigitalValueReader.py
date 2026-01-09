# digital_value_reader.py
from __future__ import annotations
from dataclasses import dataclass
from common.imports.Typing import Optional, Tuple, List
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
    value: Optional[float]
    unit: Optional[str]
    title_text: str
    title_raw: List[str]
    raw_text: List[str]
    ocr_confidence: float

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

    def _ocr_value(self, img: np.ndarray, min_val=None, max_val=None, prefer_decimal=True) -> tuple[Optional[float], list[str], float]:
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

    def _read_unit(self, img_bgr: np.ndarray) -> Optional[str]:
        roi = (0.65, 0.0, 1.0, 0.30)
        crop = _roi_crop(img_bgr, roi)
        joined, _ = self._ocr_text(crop)
        if "°" in joined or "c" in joined:
            return "°C"
        if "%" in joined:
            return "%"
        if "bar" in joined:
            return "bar"
        return None

    def _classify_display(self, img_bgr: np.ndarray) -> tuple[str, str, list[str]]:
        title_roi = (0.00, 0.00, 0.65, 0.32)
        crop = _roi_crop(img_bgr, title_roi)
        joined, raw = self._ocr_text(crop)

        temp_patterns = ["temper", "temperatur", "temp", "tomp", "tamp", "mpst", "mpct", "mps", "tompa", "tompaa", "tompat", "Teinpetalur"]
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
        unit = self._read_unit(img)

        if display_type == "unknown" and fallback_cls_id is not None:
            if fallback_cls_id == 1:
                display_type = "tempdisplay"
            elif fallback_cls_id == 0:
                display_type = "ofen"

        if self._verbose:
            print(f"[EasyOCR] display_type={display_type} unit={unit} title='{title_text}' raw_title={title_raw}")

        if display_type == "tempdisplay":
            roi = (0.10, 0.05, 0.90, 0.45)
            roi_img = _roi_crop(img, roi)
            value, raw, conf = self._ocr_value(roi_img, min_val=-50, max_val=400, prefer_decimal=True)
            if self._verbose:
                print(f"[EasyOCR] temp value={value} conf={conf} raw={raw}")
            return OcrValueResult(display_type, value, unit or "°C", title_text, title_raw, raw, conf)

        if display_type == "ofen":
            roi = (0.55, 0.65, 0.98, 0.95)
            roi_img = _roi_crop(img, roi)
            value, raw, conf = self._ocr_value(roi_img, min_val=-10, max_val=500, prefer_decimal=True)
            if self._verbose:
                print(f"[EasyOCR] ofen value={value} conf={conf} raw={raw}")
            return OcrValueResult(display_type, value, unit, title_text, title_raw, raw, conf)

        return OcrValueResult("unknown", 0.0, "%", title_text, title_raw, [], 0.0)

if __name__ == "__main__":
    from pathlib import Path
    import re

    print("[MAIN] starting digital_value_reader self-test (ALL crops)")

    CROP_DEBUG_DIR = Path("/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/Data/images/crop_debug")
    CROP_DIR = Path("/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/Data/images/crop")

    # Alle Crops sammeln
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

    # cls-id aus Dateiname robust ziehen: ..._cls0... / ..._cls1...
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
        print(" value:", result.value)
        print(" unit:", result.unit)
        print(" ocr_confidence:", result.ocr_confidence)
        print(" title_text:", result.title_text)
        print(" title_raw:", result.title_raw)
        print(" raw_text:", result.raw_text)
