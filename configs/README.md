# Configs

In diesem Ordner liegen alle Konfigurationsdateien, die das Verhalten des Systems steuern.

## Format

Alle Konfigurationen sollten im **YAML- oder JSON-Format** abgelegt werden:
- YAML bevorzugt wegen besserer Lesbarkeit
- Einheitliche Schlüsselbezeichnungen (snake_case)

Beispiele:
```yaml
mqtt:
  broker: 192.168.0.12
  port: 1883
  topic: "spot/inspection/result"
```

# Richtlinien

- Keine sensiblen Daten (Passwörter, Tokens) committen → stattdessen .env oder secrets.json

- Konfigurationen sollten über eine zentrale Loader-Funktion (utils/config.py) eingelesen werden
