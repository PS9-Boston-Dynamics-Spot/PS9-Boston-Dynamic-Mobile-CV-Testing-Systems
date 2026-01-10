# Hauptanwendung (App)

## Überblick
Die Hauptanwendung ist der zentrale Einstiegspunkt des Systems und orchestriert den vollständigen End-to-End Inspektionsprozess. Während der Application Lifespan Manager einzelne Module verknüpft und Teillogik bereitstellt, führt die App den **kompletten Workflow** von der Bildaufnahme bis zur Anomaliemeldung aus.

## Unterschied zum Lifespan Manager

**Lifespan Manager**: Stellt Bausteine und Workflow-Funktionen bereit  
**Hauptanwendung**: Nutzt diese Bausteine und führt den Gesamtprozess aus

Der Lifespan Manager ist das "Was" und "Wie", die App ist das "Wann" und "In welcher Reihenfolge".

## Vollständiger Inspektions-Workflow

### 1. Bilderfassung
Die Anwendung initiiert den Inspektionsprozess:
- Roboter fährt zur SPS-Anlage und nimmt Bild auf

### 2. Sensor-Identifikation
Das aufgenommene Bild wird analysiert, um den zu prüfenden Sensor zu identifizieren:
- ArUco-Marker ID aus Bild extrahieren
- Bei fehlender ID: Fehlerbehandlung und Abbruch
- Sensor-Kategorie bestimmen (z.B. "pressure", "temperature")

### 3. OPC UA Mapping
Verbindung zwischen visueller Erkennung und Steuerungsdaten herstellen:
- ArUco-ID über Settings Manager auf OPC UA Node-ID mappen
- Schnittstelle zur SPS-Steuerung wird hergestellt

### 4. Rohdaten-Persistierung
Datenbankverbindung wird aufgebaut und Rohdaten werden gesichert:
- Originalbild mit Metadaten (Zeitstempel, Sensor-ID) speichern
- Raw Image ID für spätere Referenzierung erhalten

### 5. Bildanalyse
Der zentrale Computer Vision Prozess wird durchgeführt:
- Analoganzeige im Bild lokalisieren und zuschneiden
- Messwert durch CV-Algorithmus auslesen
- Mit OPC UA Referenzwert abgleichen
- Validierung und ggf. Fallback-Mechanismus
- Analysiertes Bild mit extrahiertem Wert in Datenbank speichern

### 6. Anomalieerkennung
Der extrahierte Wert wird auf Abweichungen geprüft:
- Anomalie-Score berechnen basierend auf Schwellwerten
- Klassifikation als normal oder anomal
- Anomalie-Daten mit vollständigen Parametern persistieren

### 7. Reaktion und Alarm
Basierend auf dem Prüfergebnis wird die entsprechende Aktion ausgeführt:
- **Bei Anomalie**: ?????
- **Bei normaler Messung**: Bestätigung und Fortfahren zur nächsten Prüfposition

### 8. Workflow-Fortsetzung
Nach Abschluss einer Sensorprüfung:
- Iteration über weitere Sensoren (digitale Displays, weitere Anzeigen)
- Roboter navigiert zum nächsten Inspektionspunkt

## Datenbank-Session Management
Die gesamte Workflow-Ausführung erfolgt innerhalb einer konsistenten Datenbanktransaktion:
- Verbindung wird zu Beginn aufgebaut
- Alle Operationen nutzen dieselbe Session
- Bei Fehler: Rollback möglich
- Bei Erfolg: Commit aller Änderungen

## Erweiterbarkeit
Die modulare Struktur ermöglicht einfache Ergänzungen:

**Geplante Erweiterungen:**
- Verarbeitung digitaler Sensoren (LCD/LED Displays)
- Mehrere Sensoren pro Inspektionsrunde
- Roboternavigation zwischen verschiedenen Anlagen
- Automatische Missionsplanung und -ausführung

## Vorteile dieser Architektur

**Übersichtlichkeit**: Der gesamte Prozess ist linear und nachvollziehbar in einer Datei dargestellt

**Fehlerbehandlung**: Zentrale Kontrolle über den Workflow ermöglicht konsistente Fehlerbehandlung

**Testing**: Der End-to-End Prozess kann vollständig getestet werden

**Debugging**: Probleme können leicht lokalisiert werden, da der komplette Ablauf transparent ist

**Deployment**: Klarer Einstiegspunkt für die Anwendung