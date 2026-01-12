# Data Directory

Dieses Verzeichnis `/data` dient als zentrale Ablage für alle Daten, die im Rahmen des Projekts verwendet werden. Dazu gehören Bilddaten, Annotationsdateien, Sensordaten und vorbereitete Datensätze für Trainings- und Validierungszwecke.

## Struktur
```
/data
│
├── ArUco/ # ArUco Marker von der Produktionsanlage
|
├── map/ # Karte vom Dynamics Spot Controller
|
├── images/ # Kamerabilder für Prüfungen
│ ├── train/ # Trainingsdaten für CV-Modelle
│ ├── val/ # Validierungsdaten
| ├── raw/ # Rohdaten, unbearbeitet
│ └── test/ # Testdaten
│
├── labels/ # label der image für das CV Training
│ ├── train/ # Trainingsdaten Beschreibung
│ ├── val/ # Validierungs Beschreibung
│ ├── val.cache
│ └── train.cache
│
├── annotations/ # Annotationsdateien zu Bildern (Labels, Bounding Boxes, Messwerte)
│
├── sensor_data/ # Optional: Daten von Sensoren oder Roboterarmpositionen
│
│
└── processed/ # Vorverarbeitete Daten, normalisiert oder augmentiert für Modelle
```
