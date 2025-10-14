# Tests

In diesem Ordner liegen alle automatisierten Tests für das System.

## Richtlinien

- **Framework:** ??? -> pytest oder Unittest?
- **Namenskonvention:** Testdateien immer mit `test_` beginnen.  
- **Struktur:** Jeder Test sollte klar zwischen Setup, Ausführung und Überprüfung trennen (`Arrange – Act – Assert`).  
- **Mocking:** Für externe Abhängigkeiten (z. B. SDK, Kamera, Netzwerk) bitte Mock-Objekte oder Fixtures verwenden.  
    - Tests nie mit echter Hardware oder externen APIs koppeln → immer simulieren.
- **Ziel:** Jeder PR sollte nur bestehen, wenn alle Tests erfolgreich sind (`pytest -v`).

## Beispiel

```python
# Beispiel: tests/test_mqtt.py
from common.mqtt.client import MqttClient

def test_mqtt_connection(monkeypatch):
    client = MqttClient("localhost", 1883)
    monkeypatch.setattr(client, "connect", lambda: True)
    assert client.connect() is True
```