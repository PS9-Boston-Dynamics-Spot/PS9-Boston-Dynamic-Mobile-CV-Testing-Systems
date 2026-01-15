#!/usr/bin/env python3
"""Download the EasyOCR weights we rely on for offline devcontainer runs."""
from __future__ import annotations

import hashlib
import io
import os
import pathlib
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile

from easyocr.config import MODULE_PATH, detection_models, recognition_models

MODEL_DIR = pathlib.Path(os.environ.get("EASYOCR_MODEL_DIR", MODULE_PATH)) / "model"
REQUIRED_MODELS = {
    "detector_craft": detection_models["craft"],
    # Latin covers the (en, de) combo we use; ship english as a safeguard
    "recognizer_latin_g2": recognition_models["gen2"]["latin_g2"],
    "recognizer_english_g2": recognition_models["gen2"].get("english_g2"),
}


def _md5(path: pathlib.Path) -> str:
    hasher = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _download_and_extract(url: str, filename: str, destination_dir: pathlib.Path) -> pathlib.Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".zip")
    os.close(tmp_fd)
    tmp_file = pathlib.Path(tmp_path)
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
        tmp_file.write_bytes(data)
        with zipfile.ZipFile(tmp_file) as archive:
            archive.extract(filename, path=destination_dir)
    finally:
        try:
            tmp_file.unlink()
        except FileNotFoundError:
            pass
    return destination_dir / filename


def ensure_model(name: str, meta: dict[str, str]) -> None:
    filename = meta["filename"]
    url = meta["url"]
    expected_md5 = meta["md5sum"]
    target = MODEL_DIR / filename

    if target.exists():
        if expected_md5 and _md5(target) == expected_md5:
            print(f"[EasyOCR] {name}: already present")
            return
        print(f"[EasyOCR] {name}: checksum mismatch, redownloading")
        target.unlink()

    print(f"[EasyOCR] {name}: downloading from {url}")
    try:
        downloaded = _download_and_extract(url, filename, MODEL_DIR)
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to download {name} from {url}: {exc}") from exc

    if expected_md5 and _md5(downloaded) != expected_md5:
        raise RuntimeError(f"MD5 mismatch for {name} after download")


if __name__ == "__main__":
    if not REQUIRED_MODELS["recognizer_english_g2"]:
        print("[EasyOCR] english_g2 metadata missing; please update easyocr.config", file=sys.stderr)
        sys.exit(1)

    for model_name, metadata in REQUIRED_MODELS.items():
        ensure_model(model_name, metadata)
    print(f"[EasyOCR] Models stored under {MODEL_DIR}")
