from typing import Optional, Dict, Any
from configs.loader.ConfigLoader import ConfigLoader
from configs.enum.ConfigEnum import ConfigEnum, OPCUA_NODES
from configs.exceptions.MultipleIDsError import MultipleIDsError


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
    
    def getOPCUANodesbyID(self, id: int) -> Optional[str]:
        nodes = self._getNodes()
        result = []
        for key, value in nodes.items():
            if value.get(OPCUA_NODES.ARUCO_ID) == id:
                result.append(value.get(OPCUA_NODES.OPCUA_NODE))

        if len(result) > 1:
            raise MultipleIDsError(error_code=1763491580, nodes=result, id=id)

        return result[0] if result else None
