# Source Code (`src/`)
```
src/
├── core/ → zentrale Logik, State-Machine, Ablaufsteuerung
├── common/ → Alle notwendigen Module
├── common/cvision/ → Computer-Vision-Modelle und Bildverarbeitung
├── common/sdk/ → Steuerung und Missionshandling für den Laufroboter
├── common/mqtt/ → Kommunikation über MQTT
├── common/opcua/ → Kommunikation über OPC-UA
└── common/utils/ → Hilfsfunktionen, Logging, Config Loader, Fehlerhandling
```

## Entwicklungsrichtlinien

- Jede neue Funktionalität bekommt ein eigenes Modul oder eine Klasse  
- Keine Hardcodierung von Pfaden oder IP-Adressen → stattdessen Configs aus `/configs`
- Neue Unterordner immer mit:
  - einer `__init__.py` (leer reicht)#

## Beispiel: Neuer Bestandteil

Wenn du z. B. ein neues Kommunikationsprotokoll (z. B. Modbus) hinzufügen willst:

1. Neuen Ordner `common/modbus/` erstellen  
2. `__init__.py` hinzufügen (leer reicht aus)
2. `README.md` ggf. hinzufügen, der Zweck und verwendete Bibliotheken beschreibt (nicht zwangsläufig notwendig) 
3. `modbus_client.py` implementieren
4. Tests in `/tests/test_modbus.py` ergänzen  