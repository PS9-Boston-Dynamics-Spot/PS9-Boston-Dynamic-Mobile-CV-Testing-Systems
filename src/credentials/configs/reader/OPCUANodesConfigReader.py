from typing import Optional, Dict, Any, Callable
import math
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
    
    def __getScoreFunction(self, aruco_id: int) -> Optional[str]:
        matched_node = self._findNodeByID(aruco_id=aruco_id)
        return matched_node.get(OPCUA_NODES.SCORE_FUNCTION)
    
    def getScoreFunction(self, aruco_id: int) -> Optional[Callable[[float], float]]:
    
        score_function_str = self.__getScoreFunction(aruco_id=aruco_id)
        parameters = self.getParameters(aruco_id=aruco_id)

        return lambda x: eval(score_function_str, {"exp": math.exp, "pow": math.pow, **parameters, "x": x})
    
    def getParameters(self, aruco_id: int) -> Optional[dict]:
        matched_node = self._findNodeByID(aruco_id=aruco_id)
        return matched_node.get(OPCUA_NODES.PARAMETERS)

    def _getRiskManagement(self, aruco_id: int) -> dict:
        matched_node = self._findNodeByID(aruco_id=aruco_id)
        return matched_node.get(OPCUA_NODES.RISK_MANAGEMENT)
    
    def getSafeRange(self, aruco_id: int) -> Optional[float]:
        return self._getRiskManagement(aruco_id=aruco_id).get(OPCUA_NODES.SAFE_RANGE)
    
    def getUncertainRange(self, aruco_id: int) -> Optional[float]:
        return self._getRiskManagement(aruco_id=aruco_id).get(OPCUA_NODES.UNCERTAIN_RANGE)
    
    def getAnomalyRange(self, aruco_id: int) -> Optional[float]:
        return self._getRiskManagement(aruco_id=aruco_id).get(OPCUA_NODES.ANOMALY_RANGE)