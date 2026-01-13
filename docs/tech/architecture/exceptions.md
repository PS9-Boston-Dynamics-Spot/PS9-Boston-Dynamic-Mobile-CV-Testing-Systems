# Exception Handling

Aktuell wird ein traceback-ähnliches Exception-Logging bzw. -Handling eingesetzt. Dieses bietet beim Testen und Bugfixing den Vorteil, dass gezielt nach Fehlercodes gesucht werden kann, anstatt den gesamten Traceback analysieren zu müssen.

Zwar entsteht dadurch ein höherer bzw. teilweise doppelter Overhead, jedoch ist dieser Ansatz für den Produktivbetrieb deutlich besser geeignet. Fehler lassen sich so schneller identifizieren, eindeutig zuordnen und gezielt an der entsprechenden Stelle im Code beheben.


## Error Codes

Aktuell gibt es noch kein endgültiges Konzept für ein standardisiertes Error-Code-System.  
Bis zur Implementierung einer sauberen Lösung verwenden wir [**temporär Unix-Timestamps**](https://www.unixtimestamp.com/) als eindeutige Error-Codes.

### Hintergrund
Unix-Timestamps bieten den Vorteil, dass sie:
- **eindeutig** sind
- **leicht rückverfolgbar** sind im Code

Diese Vorgehensweise erleichtert die Fehlersuche während der gesamten Entwicklungsphase.