from configs.reader.OPCUANodesConfigReader import OPCUANodesConfigReader


class ArUcoIDOPCUANodeMapper:

    def __init__(self):

        self.config_reader = OPCUANodesConfigReader()
        self.overall_dict = self.config_reader.getOverallDict()
    
    def get_opcua_node_by_id(self, aruco_id: int) -> str:
        return self.config_reader.getOPCUANodebyID(aruco_id=aruco_id)