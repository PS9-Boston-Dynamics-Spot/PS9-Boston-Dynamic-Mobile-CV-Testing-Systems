# Anomalie-Erkennung

## Übersicht
Die Anomalie-Erkennung basiert auf mathematischen Funktionen, die flexibel konfiguriert und an verschiedene Sensoren und Maschinen angepasst werden können. Dieser Ansatz ermöglicht eine präzise Bewertung von Messwerten ohne den Aufwand für neuronale Netze.

## Funktionsweise

### Konfigurierbare Scoring-Funktionen
- Eine oder mehrere mathematische Funktionen werden für die Anomalie-Bewertung verwendet
- Vollständige Konfiguration über Konfigurationsdateien möglich, einschließlich aller Parameter
- Die Funktionen werden zur Laufzeit eingelesen und ausgewertet
- Jede Funktion kann individuell genutzt und angepasst werden

### Sensor- und maschinenspezifische Anpassung
Die Wahl der Scoring-Funktion ist abhängig von:
- Dem spezifischen Sensortyp
- Den Eigenschaften der überwachten Maschine
- Den erwarteten Messwertbereichen und -mustern

## Design-Philosophie

### Flexibilität und Modularität
Die Grundidee besteht darin, eine modifizierbare, flexible und modulare Scoring-Methode bereitzustellen:

- **Anpassungsfähigkeit**: Funktionen können ohne Code-Änderungen über Konfigurationsdateien angepasst werden
- **Entwicklungsfreundlich**: Bereits in der Entwicklungsphase können sinnvolle Grenzwerte festgelegt werden
- **Risikomanagement**: Ermöglicht weiche Grenzwerte statt harter Schwellenwerte, passend zum Risikomanagement-Konzept

### Vorteile gegenüber ML-Ansätzen
- **Geringerer Aufwand**: Keine umfangreiche Datensammlung und -aggregierung erforderlich
- **Kein Modelltraining**: Neuronale Netze müssen nicht trainiert werden
- **Verlässlichkeit**: Mathematisch nachvollziehbare und reproduzierbare Ergebnisse
- **Schnelle Anpassung**: Änderungen können sofort durch Konfigurationsanpassungen umgesetzt werden

## Implementierungsprozess

### 1. Datenerfassung
Im Idealfall wird eine Stichprobe an Daten gesammelt, die das normale Betriebsverhalten repräsentiert.

### 2. Datenauswertung
Die gesammelten Daten werden analysiert, um Muster und Normalverteilungen zu identifizieren.

### 3. Funktionsableitung
Aus der Datenauswertung wird eine passende mathematische Funktion abgeleitet oder modelliert, die das Normalverhalten beschreibt.

### 4. Risikomanagement-Integration
Die Funktion wird mit den Vorgaben des Risikomanagements abgeglichen und entsprechend angepasst, um:
- Falsch-positive Alarme zu minimieren
- Kritische Anomalien zuverlässig zu erkennen
- Angemessene Sicherheitsmargen einzuhalten

## Zusammenfassung

Dieser funktionsbasierte Ansatz bietet eine optimale Balance zwischen:
- **Zuverlässigkeit**: Mathematisch fundierte Anomalie-Bewertung
- **Effizienz**: Geringer Implementierungs- und Wartungsaufwand
- **Flexibilität**: Einfache Anpassung an verschiedene Szenarien
- **Nachvollziehbarkeit**: Transparente und erklärbare Entscheidungen