# Data Directory

Dieses Verzeichnis `/data` dient als zentrale Ablage für alle Daten, die im Rahmen des Projekts verwendet werden. Dazu gehören Bilddaten, Annotationsdateien, Sensordaten und vorbereitete Datensätze für Trainings- und Validierungszwecke.

## Beispiel Struktur
```
/data
│
├── images/ # Kamerabilder für Prüfungen
│ ├── train/ # Trainingsdaten für CV-Modelle
│ ├── val/ # Validierungsdaten
│ └── test/ # Testdaten
│
├── annotations/ # Annotationsdateien zu Bildern (Labels, Bounding Boxes, Messwerte)
│
├── sensor_data/ # Optional: Daten von Sensoren oder Roboterarmpositionen
│
├── raw/ # Rohdaten, unbearbeitet
│
└── processed/ # Vorverarbeitete Daten, normalisiert oder augmentiert für Modelle
```