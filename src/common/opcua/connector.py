from opcua import Client
from opcua import ua
import time

# ============================================
#   OPC UA CONNECTOR SCRIPT
# ============================================

# Server-Endpoint (z. B. "opc.tcp://localhost:4840")
OPCUA_URL = "opc.tcp://192.168.2.1:4840"

# Beispiel-Knoten (kannst du anpassen)
NODE_ID = "ns=3;s=dbAppCtrl.Hmi.Obj.EB.Proc.rActVal"

def main():
    client = Client(OPCUA_URL)
    connected = False

    try:
        print(f"🔌 Verbinde mit OPC UA Server: {OPCUA_URL}")
        client.connect() # sign with Basic256
        connected = True
        print("✅ Verbindung hergestellt")

        # Optional: Serverstatus prüfen
        try:
            status_node = client.get_node(ua.ObjectIds.Server_ServerStatus)
            status = status_node.get_value()
            print("📡 Serverstatus:", status.State)
        except Exception as e:
            print("⚠️  Konnte Serverstatus nicht abrufen:", e)

        # Beispielknoten lesen
        node = client.get_node(NODE_ID)
        print(f"🔍 Lese Wert von Node {NODE_ID}")

        while True:
            value = node.get_value()
            print(f"➡ Aktueller Wert: {value}")
            time.sleep(2)

    except Exception as e:
        print("❌ Fehler:", e)

    finally:
        if connected:
            try:
                client.disconnect()
                print("🔒 Verbindung sauber getrennt")
            except Exception as e:
                print("⚠️  Fehler beim Trennen der Verbindung:", e)
        else:
            print("ℹ️  Keine aktive Verbindung – Disconnect übersprungen")

if __name__ == "__main__":
    main()