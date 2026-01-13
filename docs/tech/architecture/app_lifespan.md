# Application Lifespan Manager

## Überblick
Der Application Lifespan Manager steuert den gesamten Lebenszyklus der Anwendung und stellt sicher, dass alle performancekritischen Komponenten während der Laufzeit kontinuierlich verfügbar sind. Zusätzlich orchestriert er die zentrale Geschäftslogik des Systems.

## Hauptaufgaben

### 1. Ressourcen-Initialisierung
Beim Anwendungsstart instanziert der Lifespan Manager ein zentrales **Initializer-Objekt**, das alle global benötigten Services einmalig lädt und für die gesamte Laufzeit bereitstellt.

**Bereitgestellte Services:**
- **Daten-Mapper**: Konvertieren Rohdaten in strukturierte Datenbank-Formate
- **Konfigurations-Manager**: Verwaltet alle Systemeinstellungen und Parameter
- **Computer Vision Komponenten**: ArUco-Erkennung, Bildvorverarbeitung, Anzeigenauslese
- **Anomalie-Engine**: Validiert Messwerte gegen definierte Schwellwerte

**Vorteil**: Durch Vorab-Initialisierung entfallen Verzögerungen beim ersten Zugriff – alle Komponenten sind sofort einsatzbereit.

### 2. Workflow-Orchestrierung
Der Lifespan Manager kapselt die gesamte Inspektionslogik in wiederverwendbaren Workflow-Funktionen, die die verschiedenen Systemmodule koordinieren:

#### Bildanalyse-Workflow
Koordiniert den kompletten Prozess vom Rohbild bis zum validierten Messwert:
- Bild zuschneiden auf relevanten Anzeigebereich
- Kalibrierung der Anzeige (Geometrie ermitteln)
- Computer Vision Analyse zur Wertextraktion
- Abgleich mit OPC UA Referenzwert
- Toleranzprüfung und Fallback-Mechanismus
- Persistierung aller Verarbeitungsschritte

#### Anomalie-Workflow
Führt die Anomalieerkennung durch und dokumentiert Ergebnisse:
- Berechnung des Anomalie-Scores basierend auf konfigurierten Algorithmen
- Klassifikation als normal oder anomal
- Speicherung mit vollständigen Metadaten (verwendete Parameter, Schwellwerte)
- Mögliche Umsetzung: Weitergabe an Alarm-System bei erkannten Abweichungen

#### Daten-Persistierung
Stellt sicher, dass alle Informationen strukturiert gespeichert werden:
- Rohdaten mit Zeitstempeln und Sensorzuordnung
- Analysierte Bilder mit extrahierten Werten
- Anomalie-Informationen mit Bewertungen

### 3. Modulübergreifende Koordination
Der Lifespan Manager fungiert als zentrale Schnittstelle zwischen den verschiedenen Systemkomponenten:

**Kommunikationsfluss:**
```
Bilderfassung → Computer Vision → OPC UA Abgleich → Anomalieerkennung → Datenspeicherung
```

Jedes Modul arbeitet isoliert, aber der Lifespan Manager stellt sicher, dass Daten korrekt zwischen den Komponenten fließen und der Gesamtworkflow konsistent abläuft.

## Architektur-Vorteile

**Performanz**: Kritische Services sind bereits initialisiert und müssen nicht bei jeder Anfrage neu geladen werden

**Konsistenz**: Zentrale Orchestrierung verhindert inkonsistente Zustände zwischen Modulen

**Wartbarkeit**: Workflow-Logik ist an einer Stelle gebündelt und nicht über das System verstreut

**Erweiterbarkeit**: Neue Workflow-Schritte können hinzugefügt werden, ohne bestehende Module zu verändern

**Nachvollziehbarkeit**: Der komplette Inspektionsprozess ist durch die Workflow-Funktionen dokumentiert und verständlich