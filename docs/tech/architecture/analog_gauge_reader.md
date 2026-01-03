# Analoge Sensorik

## Übersicht
Die analoge Sensorik wird über das vom Roboter aufgenommene Bild ausgewertet. Die Implementierung basiert auf einer hybriden Lösung, die gewichtete Modelle der ETH Zürich mit eigenen Computer-Vision-Algorithmen kombiniert.

## Komponenten der ETH Zürich

### Bildvorverarbeitung (Cropping)
Der relevante Bereich des Sensors wird aus dem Bild zugeschnitten (Crop), um die weitere Verarbeitung zu fokussieren.

**Quelle:** ETH Zürich – [analog_gauge_reader](https://github.com/ethz-asl/analog_gauge_reader)

### Winkelbestimmung (Heatmap-basiert)
Die Bestimmung von Anfangs- und Endwinkel erfolgt mittels trainierter Heatmap-Modelle. Durch diese Winkelbestimmung wird ein Mapping zwischen den Skalenwerten und den Kreiswinkeln erstellt, sodass der Messwert aus dem Winkel extrahiert werden kann. Dabei werden der Start- und Endwinkel des kleinsten bzw. größten Wertes zurückgegeben.

**Quelle:** ETH Zürich – `src/cvision/analog/AnalogGaugeCropper.py` + `src/cvision/analog/KeyPointDetector.py` + `src/cvision/analog/key_point_detection` + `src/cvision/analog/models`

## Eigene Implementierung

### Kalibrierung
Als erstes wird der analoge Sensor kalibriert, wobei das Zentrum des Sensors ermittelt wird. Dies erfolgt durch:

1. **Konturenerkennung** im zugeschnittenen Bildbereich
2. **Ellipsenerkennung** aus den gefundenen Konturen
3. **Filterung** der Ellipsen, um geeignete Kandidaten für das Zentrum zu identifizieren

### Wertextraktion
Bei der eigentlichen Wertextraktion läuft folgender Prozess ab:

1. **Kantenerkennung** zur Erkennung von Linien im Bild
2. **Filterung** der erkannten Linien anhand festgelegter Kriterien
3. **Nadelspitzen-Detektion** aus den gefilterten Linien
4. **Winkelberechnung** relativ zum Mittelpunkt
5. **Rückgabe** des ermittelten Messwerts

## Technischer Ansatz

### Hybride Lösung
Diese hybride Lösung kombiniert gewichtete Modelle der ETH Zürich (Cropping, Winkelbestimmung) mit eigenen Computer-Vision-Algorithmen (Kalibrierung, Wertextraktion) und bietet mehrere Vorteile:

**Vorteile:**
- Flexible Anpassung an verschiedene Sensortypen
- Kein umfangreiches Training eines vollständigen neuronalen Netzes erforderlich
- Gutes Verhältnis zwischen Nutzen, Aufwand und Zeitmanagement
- Kombination von ML-basierten und klassischen CV-Methoden

**Herausforderungen:**
- Empfindlichkeit gegenüber Umwelteinflüssen (z.B. Schattierungen)
- Starke Neigungswinkel der Originalaufnahme können die Extraktion beeinträchtigen oder unmöglich machen

## Entwicklungsverlauf
Ursprünglich wurden ausschließlich einfache CV-Algorithmen zur Wertextraktion verwendet. Schrittweise wurden dann die gewichteten Modelle der ETH Zürich für Cropping und Winkelbestimmung integriert, um die Genauigkeit und Robustheit zu verbessern. Die Kalibrierung und finale Wertextraktion wurden als eigene Komponenten entwickelt, um eine flexible Anpassung an verschiedene Sensortypen zu ermöglichen.