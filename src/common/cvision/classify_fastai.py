from pathlib import Path
import argparse
import csv
import sys

def main():
    parser = argparse.ArgumentParser(description="Classify images in data/images/crop using exported fastai model")
    parser.add_argument("--model", "-m", type=str, default=None, help="Path to exported fastai learner (.pkl)")
    parser.add_argument("--input", "-i", type=str, default="data/images/crop", help="Input folder with images")
    parser.add_argument("--out", "-o", type=str, default="data/images/crop/predictions.csv", help="Output CSV path")
    args = parser.parse_args()

    # lazy import so script fails clearly when fastai not installed
    try:
        from fastai.vision.all import load_learner, PILImage
    except Exception as e:
        print("Fehler: fastai nicht installiert oder Import fehlgeschlagen:", e, file=sys.stderr)
        sys.exit(2)

    # resolve model path: prefer explicit arg, sonst try common filenames under notebooks
    model_path = Path(args.model) if args.model else None
    if not model_path:
        cand = Path(__file__).parent / "notebooks"
        for fn in ("export_resnet34.pkl", "export.pkl", "export_resnet34.pth"):
            p = cand / fn
            if p.exists():
                model_path = p
                break
    if not model_path or not model_path.exists():
        print("Exportiertes Model nicht gefunden. Setze --model / Pfad prüfen.", file=sys.stderr)
        sys.exit(3)

    print("Lade Modell von", model_path)
    learn = load_learner(model_path)

    inp = Path(args.input)
    if not inp.exists() or not inp.is_dir():
        print("Input-Ordner nicht gefunden:", inp, file=sys.stderr)
        sys.exit(4)

    exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}
    images = sorted([p for p in inp.rglob("*") if p.suffix.lower() in exts])
    if not images:
        print("Keine Bilder im Ordner gefunden:", inp, file=sys.stderr)
        sys.exit(5)

    out_csv = Path(args.out)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    with out_csv.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["path", "pred", "pred_idx", "prob", "all_probs"])
        for p in images:
            try:
                img = PILImage.create(p)
                pred, pred_idx, probs = learn.predict(img)
                probs_list = [float(x) for x in probs]
                writer.writerow([str(p), str(pred), int(pred_idx), float(probs_list[int(pred_idx)]), probs_list])
            except Exception as e:
                writer.writerow([str(p), "ERROR", "-", "-", str(e)])
                print("Fehler bei", p, ":", e)

    print("Fertig. Ergebnisse in", out_csv)

if __name__ == "__main__":
    main()