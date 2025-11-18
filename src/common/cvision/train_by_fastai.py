import fastai
from fastai.vision.all import *
from PIL import Image
from pathlib import Path

# Pfade
project_root = Path(__file__).resolve().parents[3]  # 3 Ebenen hoch
data_path = project_root / 'data' / 'images' / 'data.csv'
crop_path = project_root / 'data' / 'images' / 'crop'
train_path = project_root / 'data' / 'images' / 'train'
val_path = project_root / 'data' / 'images' / 'val'
model_root = project_root / 'src' / 'common' / 'cvision' / 'models' / 'fastai_model.pkl'

# Daten laden
dls = ImageDataLoaders.from_csv(
    path=project_root,
    csv_fname=data_path,
    folder=crop_path,
    valid_pct=0.2,
    item_tfms=Resize(224),
    bs=32
)
# Modell erstellen und trainieren
learn = vision_learner(dls, resnet34, metrics=accuracy)
learn.fine_tune(5)
learn.export(model_root)

print("✅ FastAI Modelltraining abgeschlossen und gespeichert!")
