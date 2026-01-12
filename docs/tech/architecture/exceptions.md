## Error Codes

Aktuell gibt es noch kein endgültiges Konzept für ein standardisiertes Error-Code-System.  
Bis zur Implementierung einer sauberen Lösung verwenden wir [**temporär Unix-Timestamps**](https://www.unixtimestamp.com/) als eindeutige Error-Codes.

### Hintergrund
Unix-Timestamps bieten den Vorteil, dass sie:
- **eindeutig** sind
- **leicht rückverfolgbar** sind im Code

Diese Vorgehensweise erleichtert die Fehlersuche während der gesamten Entwicklungsphase.