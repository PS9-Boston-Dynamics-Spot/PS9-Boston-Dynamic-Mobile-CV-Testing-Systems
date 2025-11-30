from typing import Optional, Dict, Any, Tuple
from credentials.configs.loader.ConfigLoader import ConfigLoader
from credentials.configs.enum.ConfigEnum import ConfigEnum, OPCUA_NODES
from credentials.configs.exceptions.MultipleIDsError import MultipleIDsError
from credentials.configs.exceptions.NodeDoesNotExistError import NodeDoesNotExistError
from credentials.configs.exceptions.MinMaxValueError import MinMaxValueError


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
    
    def _findNodeByID(self, aruco_id: int) -> Dict[str, Dict[str, Any]]:
        nodes = self._getNodes()

        matched_nodes: Dict[str, Dict[str, Any]] = {}

        for node_name, props in nodes.items():
            if props.get(OPCUA_NODES.ARUCO_ID) == aruco_id:
                matched_nodes[node_name] = props

        if len(matched_nodes) > 1:
            raise MultipleIDsError(
                error_code=1763491580,
                nodes=list(matched_nodes.keys()),
                id=aruco_id
            )

        if len(matched_nodes) < 1:
            raise NodeDoesNotExistError(
                error_code=1763729190,
                aruco_id=aruco_id
            )

        node_props = next(iter(matched_nodes.values()))
        return node_props

    def getOPCUANodeByID(self, aruco_id: int) -> Optional[str]:
        matched_node = self._findNodeByID(aruco_id=aruco_id)
        return matched_node[OPCUA_NODES.OPCUA_NODE]
    
    def getValueRange(self, aruco_id: int) -> Tuple[Optional[float], Optional[float]]:
        matched_node = self._findNodeByID(aruco_id=aruco_id)

        min_value = matched_node.get(OPCUA_NODES.MIN_VALUE)
        max_value = matched_node.get(OPCUA_NODES.MAX_VALUE)

        if min_value > max_value:
            raise MinMaxValueError(
                error_code=1764536910,
                node=matched_node[OPCUA_NODES.OPCUA_NODE],
                id=aruco_id,
                min_value=min_value,
                max_value=max_value
            )
        
        return (min_value, max_value)
