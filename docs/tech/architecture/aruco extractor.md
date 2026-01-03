# ArUco Marker

## Übersicht
ArUco-Marker dienen als eindeutige Identifikatoren für Sensoren und Komponenten im System. Ihre Erkennung und Zuordnung ist essentiell für die automatisierte Verarbeitung.

## Erkennungsprozess

### 1. Bildvorverarbeitung
Das aufgenommene Bild wird zunächst auf den relevanten Bereich zugeschnitten (Crop), sodass nur der ArUco-Marker im Bildausschnitt vorhanden ist.

### 2. Marker-Auslesung
Der zugeschnittene Bildbereich wird analysiert und die eindeutige Marker-ID wird extrahiert und zurückgegeben.

### 3. Konfigurationsmapping
Die erkannte Marker-ID wird für das Mapping in der Konfigurationsdatei verwendet. Dadurch können alle notwendigen Elemente und Informationen gefunden werden, die für die weitere Verarbeitung benötigt werden:

- **CVision-Parameter**: Spezifische Bildverarbeitungseinstellungen für den jeweiligen Sensor
- **OPCUA-Knotenpunkte**: Zuordnung zu den entsprechenden OPCUA-Nodes
- **Sensor-Metadaten**: Zusätzliche Informationen wie Sensortyp, Messbereich, Einheiten etc.

## Workflow-Integration

```
Bildaufnahme → Crop auf Marker → ID-Erkennung → Config-Lookup → Sensor-Verarbeitung
```

Die ArUco-ID fungiert somit als Schlüssel, der die gesamte Sensor-Konfiguration und -Verarbeitung steuert und eine flexible, konfigurationsbasierte Zuordnung ermöglicht.