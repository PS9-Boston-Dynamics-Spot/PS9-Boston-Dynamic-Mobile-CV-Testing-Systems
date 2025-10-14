# Technologie-Abgrenzung: MQTT, OPC-UA, Boston Dynamics Spot


### MQTT (Message Queuing Telemetry Transport)
**Funktionsweise:**

MQTT funktioniert nach dem Publish-Subscribe-Modell. Es gibt einen zentralen Broker, der alle Nachrichten entgegennimmt und an die entsprechenden Clients weiterleitet. Jeder Client kann sowohl Publisher als auch Subscriber sein.

> - Primärer Fokus: Leichtgewichtige Maschine-zu-Maschine (M2M) Kommunikation
> - Einsatzgebiet: IoT-Sensornetzwerke, Mobile Geräte, Ressourcen-beschränkte Systeme
> - Data Flow: Echtzeit-Datenströme und Ereignis-basierte Nachrichten

**Wildcards:**
- Topics: Hierarchisch aufgebaut, z.B. haus/erdgeschoss/wohnzimmer/temperatur
- "+" (Single-Level): haus/erdgeschoss/+/temperatur matcht jedes Thema auf der dritten Ebene.
- "#" (Multi-Level): haus/erdgeschoss/# matcht alle Themen unter erdgeschoss

**Quality of Service (QoS)**
- QoS 0 (At most once): Nachricht wird einmal gesendet, keine Bestätigung.
- QoS 1 (At least once): Nachricht wird mindestens einmal gesendet, Bestätigung erforderlich.
- QoS 2 (Exactly once): Nachricht wird genau einmal gesendet, mit vierstufigem Bestätigungsverfahren.

**Persistente Sitzungen und Last Will**
- Persistente Sitzung: Broker speichert Subscription-Informationen und verpasste Nachrichten (bei QoS 1/2) für verbundene Clients.
- Last Will Testament (LWT): Vom Client konfigurierte Nachricht, die der Broker sendet, wenn der Client unerwartet die Verbindung verliert.

``` mermaid
graph TB
    subgraph "MQTT Broker"
        B[MQTT Broker]
    end

    subgraph "Publisher Clients"
        P1[Publisher 1]
        P2[Publisher 2]
    end

    subgraph "Subscriber Clients"
        S1[Subscriber 1]
        S2[Subscriber 2]
    end

    P1 --> |publish message to topic | B
    P2 --> |publish message to topic | B

    B --> |deliver message to subscriber | S1
    B --> |deliver message to subscriber | S2
    
```

---

### OPC UA (Open Platform Communications Unified Architecture)**

**Funktionsweise:**

OPC UA verwendet ein Client-Server-Modell, aber mit der Fähigkeit, auch Publish-Subscribe für Echtzeit-Daten zu unterstützen. Der Server stellt ein Informationsmodell bereit, das der Client durchsuchen, lesen, schreiben und überwachen kann.

> - Primärer Fokus: Strukturierte Industrieautomation und semantische Interoperabilität
> - Einsatzgebiet: Fabrikautomation, Prozesssteuerung, SCADA/MES-Integration
> - Data Flow: Zustandsdaten, Methodenaufrufe, historische Daten und Alarme

``` mermaid
graph TB
    subgraph " "
        S[OPC UA Server]
        SM[Informationsmodell]
        S --> SM
    end

    C[OPC UA Client] --> |lesen/schreiben/monitoren| S
```

**Informationsmodell:**
Das OPC UA-Informationsmodell ist objektorientiert und besteht aus:
> * Objekten: Repräsentieren reale Entitäten, z.B. eine Maschine.
> * Variablen: Eigenschaften des Objekts, z.B. Temperatur, Druck.
> * Methoden: Aktionen, die auf dem Objekt ausgeführt werden können, z.B. Start, Stop.
> * Referenzen: Beziehungen zwischen den Knoten.

**Dienste:**
OPC UA definiert eine Reihe von Diensten, die der Client aufrufen kann:
> * Sitzungsdienste: Verbindungsauf- und -abbau.
> * Lese-/Schreibdienste: Für Variablen.
> * Methodendienste: Zum Aufrufen von Methoden.
> * Subskriptionsdienste: Zum Abonnieren von Datenänderungen und Ereignissen.

**Sicherheit:**
> * Verschlüsselung: Nachrichten werden mit TLS verschlüsselt.
> * Authentifizierung: Mit Zertifikaten und/oder Benutzername/Passwort.
> * Autorisierung: Feingranulare Berechtigungen für Benutzer.

---

### Boston Dynamics Spot
**Funktionsweise:**
Spot ist ein vierbeiniger Roboter mit einer Vielzahl von Sensoren und Aktoren

> - Primärer Fokus: Physische Autonomie und mobile Datenerfassung
> - Einsatzgebiet: Inspektion, Überwachung, Datensammlung in komplexen Umgebungen
> - Data Flow: Sensorfusion, Bewegungssteuerung, Umgebungsinteraktion

**Software-Architektur**

``` mermaid
graph TB
    subgraph "Spot Software Stack"
        OS[Ubuntu Linux]
        SDK[Spot SDK]
        ROS2[ROS 2 Framework]
        APP[Anwendungen]

        OS --> SDK
        SDK --> ROS2
        ROS2 --> APP
    end

    SENS[Sensoren] --> SDK
    ACT[Aktoren] --> SDK
```

---

### ROS (Robot Operating System) !!! VEREINFACHT !!!
ROS ist kein traditionelles Betriebssystem, sondern ein Meta-Betriebssystem oder Framework für die Entwicklung von Robotik-Software. Es bietet eine Sammlung von Tools, Bibliotheken und Konventionen, um die Entwicklung komplexer Roboteranwendungen zu vereinfachen.

**Architektur:**
ROS basiert auf einem **Graph-Modell**, bei der verschiedene Prozesse (Nodes) über ein Netzwerk (oder lokal) kommunizieren. Die zentralen Konzepte sind:

> * Nodes: Unabhängige Prozesse, die eine bestimmte Aufgabe erfüllen (z.B. Sensorauslese, Motorensteuerung).
> * Messages: Datenstrukturen, die zwischen Nodes ausgetauscht werden.
> * Topics: Benannte Kanäle, über die Messages ausgetauscht werden (Publish/Subscribe).
> * Services: Request/Response-Kommunikation für synchrone Aufrufe.
> * Actions: Für länger laufende Aufgaben mit Feedback und Abbruchmöglichkeit.

``` mermaid
graph TB
    subgraph "ROS Graph"
        Node1[Node: Sensor Driver]
        Node2[Node: Control Algorithm]
        Node3[Node: Actuator Driver]
        
        Topic1[Topic: /sensor_data]
        Topic2[Topic: /control_cmd]
        
        Node1 -- publishes --> Topic1
        Topic1 -- subscribes --> Node2
        Node2 -- publishes --> Topic2
        Topic2 -- subscribes --> Node3
    end
```

**ROS-Architektur im Detail:**

``` mermaid
graph TB
    subgraph "ROS Computation Graph"
        subgraph "Nodes"
            N1[Sensor Node]
            N2[Perception Node]
            N3[Navigation Node]
            N4[Control Node]
            N5[Actuator Node]
        end
        
        subgraph "Topics"
            T1[./sensor_data]
            T2[./camera/image]
            T3[./lidar/scan]
            T4[./cmd_vel]
            T5[./motor_commands]
        end
        
        subgraph "Services"
            S1[GetMap]
            S2[SetParameters]
            S3[CalculatePath]
        end
        
        subgraph "Actions"
            A1[NavigateToGoal]
            A2[PickObject]
            A3[ExecuteTrajectory]
        end
        
        N1 --> T1
        N1 --> T2
        N1 --> T3
        
        T1 --> N2
        T2 --> N2
        T3 --> N2
        
        N2 --> T4
        T4 --> N3
        N3 --> T5
        T5 --> N4
        N4 --> N5
        
        N2 -.-> S1
        N3 -.-> S2
        N3 -.-> S3
        
        N3 -.-> A1
        N4 -.-> A2
        N4 -.-> A3
    end
```

**Node-Lifecycle und Management:**
 + **Node-Initialisierung:**
```
init() → Node erhält Namen und Namespace
    ↓
connect() → Verbindung zu ROS Master
    ↓
advertise() → Topic-Publication registrieren
    ↓
subscribe() → Topic-Subscription einrichten
    ↓
service() → Service-Server starten
    ↓
spin() → Hauptverarbeitungsschleife
```