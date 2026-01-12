# scan_and_update_val_labels.py
from pathlib import Path
import csv

images_dir = Path("/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/data/images/train")
csv_path = images_dir / "train_labels.csv"
image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff", ".webp"}

# gather image filenames (basename only), exclude the CSV itself
found = {p.name for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in image_exts}

# read existing entries (if file exists)
existing = set()
if csv_path.exists():
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=';')
        next_row = next(reader, None)  # header
        for row in reader:
            if row:
                existing.add(row[0])

# ensure CSV has header (create if missing)
if not csv_path.exists():
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["name", "label"])

# append missing image names with empty label
missing = sorted(found - existing)
if missing:
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=';')
        for name in missing:
            writer.writerow([name, ""])
    print(f"Added {len(missing)} image(s) to {csv_path}")
else:
    print("No new images to add.")