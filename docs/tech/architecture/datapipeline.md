# Datapipeline

## Input (Bildspeicherung)

Wenn ein Bild – ob Raw oder Analyzed – abgespeichert werden soll, durchläuft es folgenden Prozess:

**Hinweis:** Der gleiche Prozess gilt auch für Anomalien, mit Ausnahme der Objektspeicherung in MinIO (Schritt 2).

### Datenfluss: Von der Erfassung zur Speicherung

#### 1. Datenerfassung und Mapping
- Alle relevanten Daten (Metadaten + Bytes) werden vollständig gemappt
- Zusätzliche Metadaten werden extrahiert (z.B. Dateiformat, Content-Type)
- Alle Daten werden zusammengefasst und als ein Objekt erstellt und zurückgegeben

#### 2. Data Access Layer
Das gemappte Objekt gelangt in das Data Access Layer, welches:
- Objektnamen für MinIO erstellt
- Metadaten abspeichert
- Das Objekt selbst im Objektspeicher ablegt

#### 3. Repository Layer → IO Layer
- Das gesamte gemappte Objekt wird im Repository Layer zerlegt
- Die zerlegten Daten werden im IO Layer über die Writer-Instanzen persistiert

**Zusammenfassung Input:** Daten → Mapping → Data Access Layer → Repository Layer → IO Layer (Speicherung)

---

## Output (OPCUA-Datenabfrage)

Wenn Daten aus OPCUA abgerufen werden müssen, erfolgt der Prozess in umgekehrter Reihenfolge:

### Datenfluss: Von der Abfrage zur Rückgabe

#### 1. IO Layer: Datenabruf
Daten werden von der jeweiligen OPCUA-Node gefetcht

#### 2. Repository Layer: Objekterstellung
Das gemappte Objekt wird im Repository Layer aus den abgerufenen Daten erstellt

#### 3. Data Access Layer: Weitergabe
Das Objekt wird an das Data Access Layer zurückgegeben

#### 4. Rückgabe an Aufrufer
Das Data Access Layer gibt das Objekt unverändert an den Aufrufer zurück

**Zusammenfassung Output:** IO Layer (Abruf) → Repository Layer → Data Access Layer → Rückgabe

---

## Architektur-Übersicht

Der Output-Prozess ist die Umkehrung des Input-Prozesses:
- **Input:** Daten fließen von oben nach unten durch die Schichten zur Speicherung
- **Output:** Daten fließen von unten nach oben durch die Schichten zur Rückgabe