"""
train_and_infer.py
------------------
Dieses Skript:
  • liest labels.csv aus ../data/images/
  • trennt analoge und digitale Anzeigen
  • trainiert ein FastAI-Regressionsmodell für analoge Anzeigen
  • liest digitale Anzeigen per OCR (EasyOCR)
  • schreibt alle Ergebnisse (CSV & JSON) direkt in src/common/cvision/
"""
from fastai.vision.all import (
    ImageDataLoaders,
    Resize,
    vision_learner,
    resnet34,
    MSELossFlat,
    mae
)
import pandas as pd
import easyocr
from pathlib import Path
import re
import json

# === Lokale Pfade konfigurieren ===
CVISION_PATH = Path(__file__).resolve().parent
DATA_PATH = CVISION_PATH.parents[2] / 'data' / 'images' / 'train' # ../data/images/train

# Alle Outputs in denselben Ordner wie dieses Skript
OUTPUT_PATH = CVISION_PATH
MODEL_PATH = CVISION_PATH

# === CSV laden ===
csv_path = DATA_PATH / 'labels.csv'
if not csv_path.exists():
    raise FileNotFoundError(f"labels.csv nicht gefunden unter: {csv_path}")

df = pd.read_csv(csv_path, sep=",\s*", engine="python")
print(f"📄 Eingelesene Datensätze: {len(df)}")
print("Spalten:", df.columns.tolist())

# === Kategorisierung ===
df_analog = df[df['type'].str.contains('Analog', case=False, na=False)].copy()
df_digital = df[df['type'].str.contains('Digital', case=False, na=False)].copy()

print(f"🔧 Analoge Anzeigen: {len(df_analog)}, Digitale Anzeigen: {len(df_digital)}")

# === Zahlenwerte aus analogen Anzeigen extrahieren ===
def extract_numeric_value(val):
    if isinstance(val, str):
        match = re.search(r'(\d+(?:\.\d+)?)', val)
        if match:
            return float(match.group(1))
    return None

df_analog['value_num'] = df_analog['value'].apply(extract_numeric_value)
df_analog = df_analog.dropna(subset=['value_num'])

# === FastAI Modell trainieren ===
learn_analog = None
if len(df_analog) >= 5:
    print("\n🚀 Training des analogen Regressionsmodells startet...\n")

    dls_analog = ImageDataLoaders.from_df(
        df_analog,
        path=DATA_PATH / 'train',
        fn_col='filename',
        y_col='value_num',
        item_tfms=Resize(224),
        bs=8,
        valid_pct=0.2
    )

    learn_analog = vision_learner(
        dls_analog, resnet34,
        loss_func=MSELossFlat(),
        metrics=mae
    )

    learn_analog.fine_tune(10)
    model_file = MODEL_PATH / 'analog_regressor.pkl'
    learn_analog.export(model_file)
    print(f"✅ Analog-Regressor gespeichert unter: {model_file}")
else:
    print("⚠️ Zu wenige analoge Trainingsdaten — Training übersprungen.")

# === OCR für digitale Anzeigen ===
print("\n🧠 OCR-Erkennung für digitale Anzeigen...\n")
reader = easyocr.Reader(['de', 'en'])

ocr_results = []
for _, row in df_digital.iterrows():
    fname = row['filename']
    img_path = DATA_PATH / 'train' / fname
    try:
        ocr_texts = reader.readtext(str(img_path), detail=0)
        ocr_text = ' '.join(ocr_texts).strip()
    except Exception as e:
        ocr_text = f"ERROR: {e}"

    ocr_results.append({
        'filename': fname,
        'ocr_result': ocr_text
    })

df_ocr = pd.DataFrame(ocr_results)

# === Ergebnisse kombinieren ===
results = []

# Analoge Predictions
if learn_analog:
    for _, row in df_analog.iterrows():
        img_path = DATA_PATH / 'train' / row['filename']
        pred, _, _ = learn_analog.predict(str(img_path))
        results.append({
            'filename': row['filename'],
            'type': row['type'],
            'true_value': row['value'],
            'pred_value': round(float(pred), 2)
        })

# Digitale OCR-Ergebnisse
for _, row in df_ocr.iterrows():
    orig_row = df_digital[df_digital['filename'] == row['filename']].iloc[0]
    results.append({
        'filename': row['filename'],
        'type': orig_row['type'],
        'true_value': orig_row['value'],
        'pred_value': row['ocr_result']
    })

# === Ergebnisse speichern ===
df_results = pd.DataFrame(results)
out_csv = OUTPUT_PATH / 'predictions.csv'
df_results.to_csv(out_csv, index=False)
print(f"\n📊 Ergebnisse gespeichert unter: {out_csv}")

out_json = OUTPUT_PATH / 'predictions.json'
with open(out_json, 'w', encoding='utf-8') as f:
    json.dump(df_results.to_dict(orient='records'), f, indent=2, ensure_ascii=False)

print(f"💾 JSON-Ergebnisse gespeichert unter: {out_json}")

# === Vorschau ausgeben ===
print("\n🔍 Beispielausgabe:")
print(df_results.head(10))

print("\n✅ Pipeline abgeschlossen.")
