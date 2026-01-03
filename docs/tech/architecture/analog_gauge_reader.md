# Analoge Sensorik

## Übersicht
Die analoge Sensorik wird über das vom Roboter aufgenommene Bild ausgewertet. Dabei wird zunächst der relevante Bereich des Sensors aus dem Bild zugeschnitten (Crop). Anschließend werden in verschiedenen Abschnitten unterschiedliche Filter und Bildanpassungen angewendet, um die Messwerte zu extrahieren.

## Kalibrierung
Als erstes wird der analoge Sensor kalibriert, wobei das Zentrum des Sensors ermittelt wird. Dies erfolgt durch:

1. **Konturenerkennung** im zugeschnittenen Bildbereich
2. **Ellipsenerkennung** aus den gefundenen Konturen
3. **Filterung** der Ellipsen, um geeignete Kandidaten für das Zentrum zu identifizieren

## Winkelbestimmung
Die Bestimmung von Anfangs- und Endwinkel erfolgt mittels Heatmaps (entwickelt von der ETH Zürich: [analog_gauge_reader](https://github.com/ethz-asl/analog_gauge_reader), siehe `src/cvision/analog/key_point_detection` + `src/cvision/analog/models`). 

Durch diese Winkelbestimmung wird ein Mapping zwischen den Skalenwerten und den Kreiswinkeln erstellt, sodass der Messwert aus dem Winkel extrahiert werden kann. Dabei werden der Start- und Endwinkel des kleinsten bzw. größten Wertes zurückgegeben.

## Wertextraktion
Bei der eigentlichen Wertextraktion läuft folgender Prozess ab:

1. **Kantenerkennung** zur Erkennung von Linien im Bild
2. **Filterung** der erkannten Linien anhand festgelegter Kriterien
3. **Nadelspitzen-Detektion** aus den gefilterten Linien
4. **Winkelberechnung** relativ zum Mittelpunkt
5. **Rückgabe** des ermittelten Messwerts

## Technischer Ansatz

### Hybride Lösung
Diese hybride Lösung kombiniert gewichtete Modelle mit einfachen Computer-Vision-Algorithmen und bietet mehrere Vorteile:

**Vorteile:**
- Flexible Anpassung an verschiedene Sensortypen
- Kein umfangreiches Training eines vollständigen neuronalen Netzes erforderlich
- Gutes Verhältnis zwischen Nutzen, Aufwand und Zeitmanagement

**Herausforderungen:**
- Empfindlichkeit gegenüber Umwelteinflüssen (z.B. Schattierungen)
- Starke Neigungswinkel der Originalaufnahme können die Extraktion beeinträchtigen oder unmöglich machen

## Entwicklungsverlauf
Ursprünglich wurden ausschließlich einfache CV-Algorithmen zur Wertextraktion verwendet. Schrittweise wurden dann die gewichteten Modelle der ETH Zürich integriert, um die Genauigkeit und Robustheit zu verbessern.