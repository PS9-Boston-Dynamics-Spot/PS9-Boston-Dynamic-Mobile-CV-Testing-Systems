# CVision

## WICHTIG!!!!

Phyton Version 3.10-3.11 -> sonst Probleme mit FastAI.
PIP immer voher aktualisieren mit -> pip install --upgrade pip

## Installation von torch:

1. pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
2. pip install fastai easyocr pandas opencv-python

Hinweis: Pandas vermeiden da zu Komplex


## Bilddaten

Bilder von SPOT: /raw
Bilder welche bereits durch die Anzeigenerkennung "detect_and_crop.py" gelaufen sind: /crop
Bilder zum trainieren des CV Model: /train
Bilder zur Validierung: /val


## Skript 

Bildvorbearbeitung funktioniert mit:
detect_and_crop.py  -> Schneiden der Bilder im Ordner images/raw und speicherung in images/crop (Anzeigenerkennung)

CV mit YOLO:

YOLO nutzt Bilddateien welche mit einem Label makiert sind. In diesen Label sind Koordinaten und Bezeichnungen des Bildes enthalten. Für uns aber unnötig, da wir die Bilder bereits richtig Croppen und dann mit FastAi oder Torch Auswerten wollen.

train_by_yolo.py            -> mit YOLO (ungeeignet)
    auto_label_train.py       -> erzeugung von Text Dateien für die Trainingsfotos
    auto_label_train.py       -> erzeugung von Text Dateien für die Validierungsfotos

Neu:
torch_test.py       -> Test für erfolgreiche Installation von Torch Bibliotek
train_by_fastai     -> Training des Models mittels FastAI

Todo:

classify_fastai.py  -> Klassifizierung Anzeige mit trainierten Model
write_info_in_csv.py -> Erstellung einer Auswertung der 3 Anzeigen mit Anzeigekategorie und gelesenen Werten