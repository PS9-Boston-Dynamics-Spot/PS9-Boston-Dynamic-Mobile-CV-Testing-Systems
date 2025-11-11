from typing import Any
from db.opcua.connector.OPCUAConnector import OPCUAConnector


class OPCUAReader:
    def __init__(self):
        self.opcua_connector = OPCUAConnector()
        self.client = self.opcua_connector.connect()

    def read_node(self, node_id: str) -> Any:
        return self.client.get_node(node_id).get_value()
