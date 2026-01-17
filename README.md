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

---

## Setup

Um das Projekt einzurichten und zu nutzen, folge den Anleitungen in den jeweiligen Dokumenten:

- **Installation:** [Install](./docs/setup/install.md) – beschreibt, wie das Projekt in einer Container-Umgebung eingerichtet wird.  
- **Nutzung:** [Usage](./docs/setup/usage.md) – zeigt, wie du das Projekt startest, testest und betreibst.

---

## Team & Contributors

### Projektleitung
- **Prof. Dr. Dirk Reichelt** – Auftraggeber
- **Felix Fritzsche** - Projektbetreuer

### Entwicklungsteam

<table>
  <tbody>
    <tr>
      <td>
        <a href="https://github.com/laurenzzzzzz">
          <img src="https://avatars.githubusercontent.com/laurenzzzzzz" width="56" style="border-radius:50%;" />
        </a>
      </td>
      <td>
        <a href="https://github.com/laurenzzzzzz"><kbd>Laurenz Born</kbd></a><br/>
        <sub>Robot Motion · Control / Software</sub>
      </td>
    </tr>
    <tr>
      <td>
        <a href="https://github.com/Johann0001">
          <img src="https://avatars.githubusercontent.com/Johann0001" width="56" style="border-radius:50%;" />
        </a>
      </td>
      <td>
        <a href="https://github.com/Johann0001"><kbd>Johann Schmidt</kbd></a><br/>
        <sub>Robot Motion · Control / Software</sub>
      </td>
    </tr>
    <tr>
      <td>
        <a href="https://github.com/Jannes05">
          <img src="https://avatars.githubusercontent.com/Jannes05" width="56" style="border-radius:50%;" />
        </a>
      </td>
      <td>
        <a href="https://github.com/Jannes05"><kbd>Jannes Lehmann</kbd></a><br/>
        <sub>Machine Learning · Computer Vision · Config + Env Manager</sub>
      </td>
    </tr>
    <tr>
      <td>
        <a href="https://github.com/s87089">
          <img src="https://avatars.githubusercontent.com/s87089" width="56" style="border-radius:50%;" />
        </a>
      </td>
      <td>
        <a href="https://github.com/s87089"><kbd>Justus Müller</kbd></a><br/>
        <sub>Machine Learning · Computer Vision · Project Management</sub>
      </td>
    </tr>
    <tr>
      <td>
        <a href="https://github.com/paulagra">
          <img src="https://avatars.githubusercontent.com/paulagra" width="56" style="border-radius:50%;" />
        </a>
      </td>
      <td>
        <a href="https://github.com/paulagra"><kbd>Paula Grahlow</kbd></a><br/>
        <sub>Testing</sub>
      </td>
    </tr>
    <tr>
      <td>
        <a href="https://github.com/TilG7">
          <img src="https://avatars.githubusercontent.com/TilG7" width="56" style="border-radius:50%;" />
        </a>
      </td>
      <td>
        <a href="https://github.com/TilG7"><kbd>Til Guhlmann</kbd></a><br/>
        <sub>Project Recorder</sub>
      </td>
    </tr>
    <tr>
      <td>
        <a href="https://github.com/AxdeExpe">
          <img src="https://avatars.githubusercontent.com/AxdeExpe" width="56" style="border-radius:50%;" />
        </a>
      </td>
      <td>
        <a href="https://github.com/AxdeExpe"><kbd>Kevin Pietzsch</kbd></a><br/>
        <sub>Infrastructure & Tooling · Computer Vision · Anomaly Detection · Datapipeline</sub>
      </td>
    </tr>
  </tbody>
</table>




---

