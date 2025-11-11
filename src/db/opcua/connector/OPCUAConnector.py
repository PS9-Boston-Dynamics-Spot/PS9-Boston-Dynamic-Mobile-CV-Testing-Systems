from opcua import Client
import socket
from configs.reader.OPCUAConfigReader import OPCUAConfigReader
from db.opcua.exceptions.DNSError import DNSError
from db.opcua.exceptions.OPCUAConnectionRefusedError import OPCUAConnectionRefusedError
from db.opcua.exceptions.ConnectionError import ConnectionError


class OPCUAConnector:
    def __init__(self):
        self.opcua_config_reader = OPCUAConfigReader()
        self.ip = self.opcua_config_reader.getIp()
        self.port = self.opcua_config_reader.getPort()
        self.protocol = self.opcua_config_reader.getProtocol()
        self.timeout = self.opcua_config_reader.getTimeout()
        self.client = None

        self.url = f"{self.protocol}://{self.ip}:{self.port}"

    def __create_client(self) -> Client:
        if not self.client:
            self.client = Client(url=self.url, timeout=self.timeout)
        return self.client

    def connect(self) -> Client:
        try:
            self.client = self.__create_client()
            self.client.connect()
            return self.client
        except socket.gaierror as e:
            raise DNSError(exception=e, url=self.url, error_code=1762789770)
        except ConnectionRefusedError as e:
            raise OPCUAConnectionRefusedError(
                exception=e, url=self.url, error_code=1762789780
            )
        except Exception as e:
            raise ConnectionError(exception=e, url=self.url, error_code=1762789790)

    def disconnect(self) -> None:
        self.client.disconnect()


client = Client("opc.tcp://192.168.2.1:4840")
client.connect()
temperature = client.get_node(
    'ns=3;s="dbAppCtrl"."Hmi"."Obj"."EB"."Proc"."rActVal"'
).get_value()
print(f"Ofen Temperatur: {temperature}")
client.disconnect()
