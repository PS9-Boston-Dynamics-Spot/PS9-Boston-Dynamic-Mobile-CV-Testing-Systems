from opcua import Client
import socket
from credentials.manager.UnifiedCredentialsManager import UnifiedCredentialsManager
from db.opcua.exceptions.DNSError import DNSError
from db.opcua.exceptions.OPCUAConnectionRefusedError import OPCUAConnectionRefusedError
from db.opcua.exceptions.ConnectionError import ConnectionError


class OPCUAConnector:
    def __init__(self):
        self.credentials_manager = UnifiedCredentialsManager()
        self.opcua_credentials = self.credentials_manager.getOPCUACredentials()

        self.ip = self.opcua_credentials["ip"]
        self.port = self.opcua_credentials["port"]
        self.protocol = self.opcua_credentials["protocol"]
        self.timeout = self.opcua_credentials["timeout"]
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
