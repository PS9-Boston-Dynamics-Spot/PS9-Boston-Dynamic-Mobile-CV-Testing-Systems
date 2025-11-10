from opcua import Client
from configs.reader.OPCUAConfigReader import OPCUAConfigReader


class OPCUAConnector:
    def __init__(self):
        self.opcua_config_reader = OPCUAConfigReader()
        self.ip = self.opcua_config_reader.getIp()
        self.port = self.opcua_config_reader.getPort()
        self.protocol = self.opcua_config_reader.getProtocol()
        self.timeout = self.opcua_config_reader.getTimeout()

        self.url = f"{self.protocol}://{self.ip}:{self.port}"

    def __create_client(self) -> Client:
        if not self.client:
            self.client = Client(url=self.url, timeout=self.timeout)
        return self.client
    
    def connect(self) -> Client:
        self.client = self.__create_client()
        self.client.connect()
        return self.client
    
    def disconnect(self) -> None:
        self.client.disconnect()


# client = Client("opc.tcp://192.168.2.1:4840")
# client.connect()
# temperature = client.get_node("ns=3;s=\"dbAppCtrl\".\"Hmi\".\"Obj\".\"EB\".\"Proc\".\"rActVal\"").get_value()
# print(f"Ofen Temperatur: {temperature}")
# client.disconnect()