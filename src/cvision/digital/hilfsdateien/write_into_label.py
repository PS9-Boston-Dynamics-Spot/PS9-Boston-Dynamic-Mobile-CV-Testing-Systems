from pathlib import Path

# Mapping: Ordnername oder Keyword im Dateinamen → Klassen-ID
CLASS_MAP = {
    "digital_ac": 0,
    "analog_pressure": 1,
    "digital_temp": 2,
    "not_category": 3,
}

for split in ["train", "val"]:
    img_dir = Path(f"data/images/{split}")
    label_dir = Path(f"data/labels/{split}")
    label_dir.mkdir(parents=True, exist_ok=True)

    for img_path in img_dir.glob("*.jpg"):
        # Klasse anhand des Dateinamens bestimmen
        cls = None
        for key, cid in CLASS_MAP.items():
            if key in img_path.stem:
                cls = cid
                break
        if cls is None:
            cls = 3  # default "not_category"

        label_path = label_dir / f"{img_path.stem}.txt"
        label_path.write_text(f"{cls} 0.5 0.5 1 1\n")

print("✅ Dummy-Labels erstellt (ein Objekt pro Bild, ganze Fläche).")
