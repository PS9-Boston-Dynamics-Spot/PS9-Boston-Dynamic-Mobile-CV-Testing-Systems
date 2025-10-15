# Projektseminar im WS 25/26

## Mobile Prüfsysteme für zyklische Computer Vision Prüfvorgänge

### Ausgangslage / Problemstellung

In der Fertigungsindustrie stellen Qualitätssicherungen, Prüf- und Kontrollprozesse eine zentrale Säule in der Bereitstellung von hochwertigen Produkten und stabilen Prozessen dar.  
Zur Durchführung von Prüfungen werden verschiedene Prüfmittel und Methoden verwendet.  
Neben manuellen Prüfprozessen werden kamerabasierte klassische Vision Anwendungen genutzt, um die Qualität von Produkten zu erfassen. Diese sind i.d.R. statisch und benötigen eine Relativbewegung des Prüfobjektes durch ihren Sichtbereich. Mobile Prüfsysteme sollen Materialfluss unabhängig Prüfungen ermöglichen, die idealerweise autonom Stichprobenprüfungen oder Prozessüberwachungen durchführen. Neben manuellen mobilen Prüfungen durch Mitarbeitende mit mobilen Endgeräten sind fahrerlose Transportsysteme oder Laufroboter aufgrund ihrer Flexibilität für Inspektionsaufgaben qualifiziert.

Aufgrund verschiedener Sensoren, integrierten Manipulatoren und vorhandenen Kamerasystemen sowie vorhandener APIs sind verschiedenste Prüfszenarien realisierbar.

---

### Aufbau des Projektseminars:

1. Sie erhalten eine Einführung in mobile Prüfsysteme und den Umgang mit Boston Dynamics Spots.

2. Sie erstellen automatisierbare Missionen für Laufroboter, die über eine API oder SDK gestartet werden können.

3. Sie integrieren eine Positionierbarkeit des Roboterarms im Raum für definierte Prüfpositionen über eine API oder SDK.

4. Sie integrieren die Ansteuerung in eine State-Maschine, um Prüfungen zu starten, und ein Interface, um Bilddaten empfangen zu können.

5. Sie entwickeln eine Computer Vision Anwendung, um eine Anzeige an einer Maschine im IIoT-Testbed auszulösen.

6. Sie validieren ihre Bilderkennung durch die Abfrage der erkannten Messwerte über eine Schnittstelle wie MQTT/OPC-UA mit der Steuerung der Maschine.

7. Sie konzipieren und implementieren eine Anomalie-Erkennung bei Abweichungen von definierten Messwertbereichen.
