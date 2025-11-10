from db.opcua.reader.OPCUAReader import OPCUAReader
from configs.reader.OPCUANodesConfigReader import OPCUANodesConfigReader

class OPCUARepository:
    def __init__(self):
        self.reader = OPCUAReader()
        self.config_reader = OPCUANodesConfigReader()

    def get_oven_temperature(self, node_id: str) -> float:
        node_id = self.config_reader.getOvenNode()
        return self.reader.read_node(node_id)