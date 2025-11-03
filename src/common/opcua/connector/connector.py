from opcua import Client

client = Client("opc.tcp://192.168.2.1:4840")
client.connect()
temperature = client.get_node("ns=3;s=\"dbAppCtrl\".\"Hmi\".\"Obj\".\"EB\".\"Proc\".\"rActVal\"").get_value()
print(f"Ofen Temperatur: {temperature}")
client.disconnect()