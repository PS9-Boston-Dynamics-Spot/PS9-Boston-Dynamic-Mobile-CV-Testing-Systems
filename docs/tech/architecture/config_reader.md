# Credentials Manager

## Überblick
Der Credentials Manager ist zuständig für die zentrale Verwaltung aller Authentifizierungsdaten der verwendeten Module und Dienste.

## Funktionsweise
Der Manager verarbeitet Zugangsdaten aus verschiedenen Quellen und stellt diese gebündelt für die Anwendung bereit:

**Hauptaufgaben:**
- Einlesen von Konfigurationsdateien (YAML, ENV)
- Verwaltung von Zugangsdaten für externe Dienste (z.B. MinIO, OPC UA Server, Datenbanken)
- Zusammenführung der Credentials in ein einheitliches Datenpaket
- Bereitstellung der Authentifizierungsinformationen über eine zentrale Schnittstelle

**Beispiel für verwaltete Credentials:**
- **MinIO**: Access Key, Secret Key, Endpoint
- **OPC UA**: Server-URL, Username, Password
- **Datenbank**: Connection String, Credentials

## Sicherheitshinweise
Credentials werden ausschließlich aus geschützten Konfigurationsdateien oder Umgebungsvariablen geladen und niemals im Code hartcodiert.

---

# Settings Manager

## Überblick
Der Settings Manager übernimmt die Verwaltung und Interpretation aller Anwendungskonfigurationen und ist deutlich umfangreicher als der Credentials Manager.

## Funktionsweise
Der Settings Manager verarbeitet komplexe Konfigurationsstrukturen und stellt anwendungsspezifische Einstellungen bereit:

**Hauptaufgaben:**
- Parsen und Validieren von Konfigurationsdateien
- Interpretation der Anomalie-Erkennungsparameter (Schwellwerte, Toleranzbereiche, Algorithmen)
- Verwaltung von Sensor-Mappings (ArUco-ID zu OPC UA Node-ID)
- Konfiguration der Computer Vision Pipeline (Modellparameter, Bildverarbeitungseinstellungen)
- Bereitstellung von Laufzeit-Parametern für alle Systemkomponenten

## Komplexität
Der Settings Manager verarbeitet deutlich mehr Daten als der Credentials Manager, insbesondere durch:

**Anomalie-Konfiguration:**
- Schwellwerte pro Sensortyp
- Statistische Verteilungsparameter
- Risikomanagement

**Vision-Konfiguration:**
- Bildvorverarbeitungsparameter
- Uco-Erkennungseinstellungen
- Kalibrierungsdaten

**System-Konfiguration:**
- Datenbank-Schemas
- MinIO-Bucket-Strukturen