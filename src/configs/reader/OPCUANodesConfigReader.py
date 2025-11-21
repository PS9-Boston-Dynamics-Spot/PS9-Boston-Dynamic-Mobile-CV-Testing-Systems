from typing import Optional
from configs.loader.ConfigLoader import ConfigLoader
from configs.enum.ConfigEnum import ConfigEnum, OPCUA_NODES
from configs.exceptions.MultipleIDsError import MultipleIDsError
from configs.exceptions.NodeDoesNotExistError import NodeDoesNotExistError

class OPCUANodesConfigReader(ConfigLoader):
    def __init__(self):
        super().__init__()
        self.__config = self.load_config(ConfigEnum.OPCUA_NODES_CONFIG)

    def getOverallDict(self) -> Optional[str]:
        value = self.__config.get(OPCUA_NODES.OVERALL_DICT)
        return value
    
    def _getNodes(self) -> dict:
        value = self.__config.get(OPCUA_NODES.NODES)
        if not isinstance(value, dict):
            return {}
        return value
    
    def getOPCUANodebyID(self, aruco_id: int) -> Optional[str]:
        nodes = self._getNodes()
        result = []

        for key, value in nodes.items():
            if value.get(OPCUA_NODES.ARUCO_ID) == aruco_id:
                result.append(value.get(OPCUA_NODES.OPCUA_NODE))

        if len(result) > 1:
            raise MultipleIDsError(error_code=1763491580, nodes=result, id=aruco_id)
        
        if len(result) <= 1:
            raise NodeDoesNotExistError(error_code=1763729190, aruco_id=aruco_id)

        return result[0]
