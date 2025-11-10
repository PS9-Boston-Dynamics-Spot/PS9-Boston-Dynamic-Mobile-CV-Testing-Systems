# CVision

## WICHTIG!!!!

Phyton Version 3.10-3.11 -> sonst Probleme mit FastAI.
PIP immer voher aktualisieren mit -> pip install --upgrade pip

## Installation von torch:

1. pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
2. pip install fastai easyocr pandas opencv-python

-dictionarys verwenden anstatt pandas  https://www.w3schools.com/python/python_dictionaries.asp


## Bilddaten

Aktuell noch in /data/images/train

Bilder von Spot: /data/images/raw


## Skript 

VERALTET:   train_and_infer.py -> Erste CV Test mit FastAI
            predictions.csv
            predictions.json


auto_label.py       -> erzeugung von Text Dateien für die Fotos
classify_fastai.py  -> Klassifizierung Anzeige
detect_and_crop.py  -> Schneiden der Bilder zur Klassifizierung
labels.py           -> Erstellung raw Labels
torch_test.py       -> Test für erfolgreiche Installation von Torch

