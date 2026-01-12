from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from common.imports.Typing import Optional, Tuple, List
from datetime import datetime
import os

import cv2
import numpy as np
from ultralytics import YOLO


# ---------- Byte utils ----------
def bgr_from_bytes(image_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image bytes (cv2.imdecode returned None).")
    return img


def jpg_bytes_from_bgr(img_bgr: np.ndarray, quality: int = 95) -> bytes:
    ok, buf = cv2.imencode(".jpg", img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        raise ValueError("Could not encode image to jpg bytes.")
    return buf.tobytes()


def sharpness_quality_0_1(img_bgr: np.ndarray) -> float:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return min(lap_var / 500.0, 1.0)


# ---------- DTOs ----------
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


# ---------- DebugWriter ----------
@dataclass
class DebugWriter:
    out_dir: Path
    enabled: bool = True
    verbose: bool = True  # <-- neu

    def __post_init__(self) -> None:
        if not self.enabled:
            if self.verbose:
                print("[DebugWriter] disabled")
            return

        # Ordner anlegen
        self.out_dir.mkdir(parents=True, exist_ok=True)

        # Schreibtest
        try:
            test_file = self.out_dir / ".write_test"
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink(missing_ok=True)
            writable = True
        except Exception as e:
            writable = False
            if self.verbose:
                print(f"[DebugWriter] ERROR: out_dir not writable: {self.out_dir} ({e})")

        if self.verbose:
            print(f"[DebugWriter] enabled={self.enabled}")
            print(f"[DebugWriter] out_dir={self.out_dir}")
            print(
                f"[DebugWriter] exists={self.out_dir.exists()} "
                f"is_dir={self.out_dir.is_dir()} writable={writable}"
            )

            # Häufiger Fehler: Data vs data
            alt = (
                Path(str(self.out_dir).replace("/Data/", "/data/"))
                if "/Data/" in str(self.out_dir)
                else None
            )
            if alt and alt != self.out_dir:
                print(
                    "[DebugWriter] hint: check path case-sensitivity. "
                    f"Alternative would be: {alt}"
                )

    def write(self, crop: CropResult, extra_txt_lines: Optional[List[str]] = None) -> None:
        if not self.enabled:
            return

        safe_source = "".join(c if c.isalnum() or c in "-_." else "_" for c in crop.source_name)
        base = f"{safe_source}_det{crop.idx}_cls{crop.cls_id}"

        img_path = self.out_dir / f"{base}.jpg"
        txt_path = self.out_dir / f"{base}.txt"

        img_path.write_bytes(crop.crop_bytes)

        lines = [
            f"created_at_utc: {datetime.utcnow().isoformat()}Z",
            f"source_name: {crop.source_name}",
            f"idx: {crop.idx}",
            f"class_id: {crop.cls_id}",
            f"confidence: {crop.conf:.4f}",
            f"bbox_xyxy: {list(crop.bbox_xyxy)}",
            f"crop_format: {crop.crop_format}",
            f"crop_content_type: {crop.crop_content_type}",
            f"quality_image: {crop.quality_image:.3f}",
        ]
        if extra_txt_lines:
            lines.extend(extra_txt_lines)

        txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        if self.verbose:
            print(f"[DebugWriter] wrote: {img_path.name} + {txt_path.name}")


# ---------- YOLO Cropper ----------
class YoloDisplayCropper:
    """
    Byte-in -> YOLO detect -> crop bytes out
    Optional: DebugWriter schreibt Crop + TXT.

    Änderung: gibt maximal 2 Crops zurück (beste Box pro Klasse, dann Top-2 nach Conf).
    """

    def __init__(
        self,
        model_path: str = os.path.join(os.getcwd(), "src/cvision/digital/models/display_cropper.pt"),
        conf: float = 0.30,
        jpeg_quality: int = 95,
        debug: Optional[DebugWriter] = None,
        verbose: bool = True,
    ):
        self._model = YOLO(model_path)
        self._conf = conf
        self._jpeg_q = jpeg_quality
        self._debug = debug
        self._verbose = verbose

        if self._verbose:
            print("[YoloDisplayCropper] init")
            print(f"[YoloDisplayCropper] model_path={model_path}")
            print(f"[YoloDisplayCropper] conf={conf} jpeg_quality={jpeg_quality}")
            print(f"[YoloDisplayCropper] debug_enabled={bool(debug and debug.enabled)}")
            if debug is not None:
                print(f"[YoloDisplayCropper] debug_out_dir={debug.out_dir}")

    def crop_from_bytes(self, raw_image_bytes: bytes, source_name: str = "raw") -> List[CropResult]:
        if self._verbose:
            print(f"\n[YoloDisplayCropper] crop_from_bytes source={source_name} bytes={len(raw_image_bytes)}")

        img = bgr_from_bytes(raw_image_bytes)

        # YOLO inference
        res = self._model(img, conf=self._conf)[0]

        if self._verbose:
            num_boxes = 0 if res.boxes is None else len(res.boxes)
            print(f"[YoloDisplayCropper] detections={num_boxes}")

        crops: List[CropResult] = []

        if res.boxes is None or len(res.boxes) == 0:
            if self._verbose:
                print("[YoloDisplayCropper] WARNING: no boxes detected -> no crops -> nothing to debug-write")
            return crops

        # Auswahl: max. 2 Crops best box per class_id (highest conf)
        best_by_cls = {}
        for b in res.boxes:
            cls_id = int(b.cls)
            conf = float(b.conf) if b.conf is not None else 0.0
            if (cls_id not in best_by_cls) or (conf > best_by_cls[cls_id][0]):
                best_by_cls[cls_id] = (conf, b)

        # take best per class, then sort by confidence desc, then keep max 2
        selected_boxes = [pair[1] for pair in best_by_cls.values()]
        selected_boxes = sorted(selected_boxes, key=lambda bb: float(bb.conf), reverse=True)[:2]

        # Crops nur für selected_boxes erzeugen
        for idx, b in enumerate(selected_boxes):
            cls_id = int(b.cls)
            conf = float(b.conf) if b.conf is not None else 0.0
            x1, y1, x2, y2 = map(int, b.xyxy[0])

            crop_bgr = img[y1:y2, x1:x2]
            if crop_bgr.size == 0:
                if self._verbose:
                    print(f"[YoloDisplayCropper] skip empty crop idx={idx} bbox={(x1, y1, x2, y2)}")
                continue

            q_img = sharpness_quality_0_1(crop_bgr)
            crop_bytes = jpg_bytes_from_bgr(crop_bgr, quality=self._jpeg_q)

            cr = CropResult(
                source_name=source_name,
                idx=idx,
                cls_id=cls_id,
                conf=conf,
                bbox_xyxy=(x1, y1, x2, y2),
                crop_bytes=crop_bytes,
                crop_content_type="image/jpeg",
                crop_format="jpg",
                quality_image=q_img,
            )
            crops.append(cr)

            if self._verbose:
                print(
                    f"[YoloDisplayCropper] crop idx={idx} cls={cls_id} "
                    f"conf={conf:.3f} q_img={q_img:.3f} bytes={len(crop_bytes)}"
                )

            if self._debug:
                self._debug.write(cr)

        if self._verbose:
            print(f"[YoloDisplayCropper] total_crops={len(crops)}")

        return crops


if __name__ == "__main__":
    
    MODEL_PATH = "runs_cv_model_digital_display/spot_cv_model_v2/weights/best.pt"
    # --- konfig für standalone test ---
    #local debug Path
    #RAW_DIR = Path("/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/Data/images/raw")
    #projekt Path
    RAW_DIR = Path("/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/src/common/sdk/spot_bilder")
    #debug Path
    DEBUG_DIR = Path("/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/Data/images/crop_debug")

    print("[MAIN] starting digital_cropper self-test")
    print(f"[MAIN] model_path={MODEL_PATH}")
    print(f"[MAIN] raw_dir={RAW_DIR} exists={RAW_DIR.exists()}")

    # Nimmt das erste JPG aus RAW_DIR
    #lokal debug Path
    #images = sorted(list(RAW_DIR.glob("*.jpg")))
    #projekt Path
    images = sorted(list(RAW_DIR.glob("spot.jpg")))
    if not images:
        print(f"[MAIN] ERROR: no .jpg found in {RAW_DIR}")
        raise SystemExit(1)

    img_path = images[0]
    print(f"[MAIN] using image: {img_path}")

    raw_bytes = img_path.read_bytes()
    print(f"[MAIN] read bytes: {len(raw_bytes)}")

    dbg = DebugWriter(out_dir=DEBUG_DIR, enabled=True, verbose=True)

    cropper = YoloDisplayCropper(
        model_path=MODEL_PATH,
        conf=0.30,
        jpeg_quality=95,
        debug=dbg,
        verbose=True,
    )

    crops = cropper.crop_from_bytes(raw_bytes, source_name=img_path.stem)
    print(f"[MAIN] crops returned: {len(crops)}")

    if crops:
        print(
            "[MAIN] example crop:",
            crops[0].source_name,
            crops[0].cls_id,
            crops[0].conf,
            len(crops[0].crop_bytes),
        )
        print(f"[MAIN] debug output should be in: {DEBUG_DIR}")
    else:
        print("[MAIN] WARNING: 0 crops -> nothing written. (YOLO detected nothing on this image)")
