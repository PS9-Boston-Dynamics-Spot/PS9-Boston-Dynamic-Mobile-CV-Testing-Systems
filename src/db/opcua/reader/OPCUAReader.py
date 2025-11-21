from typing import Any
from db.opcua.connector.OPCUAConnector import OPCUAConnector
from opcua import ua
from db.opcua.exceptions.NodeNotFoundError import NodeNotFoundError
from db.opcua.exceptions.ReaderError import ReaderError


class OPCUAReader:
    def __init__(self):
        self.opcua_connector = OPCUAConnector()
        self.client = self.opcua_connector.connect()

    def read_node(self, node_id: str) -> Any:
        try:
            return self.client.get_node(nodeid=node_id).get_value()
        except ua.UaStatusCodeError as e:
            raise NodeNotFoundError(exception=e, node_id=node_id, error_code=1762858720)
        except Exception as e:
            raise ReaderError(exception=e, node_id=node_id, error_code=1762858730)
