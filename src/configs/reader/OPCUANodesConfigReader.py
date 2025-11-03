from typing import Optional, Dict, Any
from configs.loader.ConfigLoader import ConfigLoader
from configs.enum.ConfigEnum import ConfigEnum, OPCUA_NODES

class OPCUANodesConfigReader(ConfigLoader):
    def __init__(self):
        super().__init__()
        self.__config = self.load_config(ConfigEnum.OPCUA_NODES_CONFIG)

    def _getOPCUANodes(self) -> Dict[str, Any]:
        value = self.__config.get(OPCUA_NODES.NODES)
        if not isinstance(value, dict):
            return {}
        return value

    def getOvenNode(self) -> Optional[str]:
        return self._getOPCUANodes().get(OPCUA_NODES.OVEN_NODE)