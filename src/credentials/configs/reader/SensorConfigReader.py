from common.imports.Typing import Optional, Dict, Any, Callable, Tuple
import math
from credentials.configs.loader.ConfigLoader import ConfigLoader
from credentials.configs.enum.ConfigEnum import ConfigEnum, SENSOR_KEYS
from credentials.configs.exceptions.MultipleIDsError import MultipleIDsError
from credentials.configs.exceptions.NodeDoesNotExistError import NodeDoesNotExistError
from credentials.configs.exceptions.MinMaxValueError import MinMaxValueError


class SensorConfigReader(ConfigLoader):
    def __init__(self):
        super().__init__()
        self.__config = self.load_config(ConfigEnum.SENSOR_KEYS_CONFIG)

    def getOverallDict(self) -> Optional[str]:
        value = self.__config.get(SENSOR_KEYS.OVERALL_DICT)
        return value

    def _getNodes(self) -> dict:
        value = self.__config.get(SENSOR_KEYS.NODES)
        if not isinstance(value, dict):
            return {}
        return value

    def _findNodeByID(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Dict[str, Dict[str, Any]]:
        nodes = self._getNodes()
        matched_nodes: Dict[str, Dict[str, Any]] = {}

        for node_name, props in nodes.items():
            if aruco_id is None:
                if allow_missing and SENSOR_KEYS.ARUCO_ID not in props:
                    matched_nodes[node_name] = props
            else:
                if props.get(SENSOR_KEYS.ARUCO_ID) == aruco_id:
                    matched_nodes[node_name] = props

        if len(matched_nodes) > 1:
            raise MultipleIDsError(
                error_code=1763491580, nodes=list(matched_nodes.keys()), id=aruco_id
            )

        if not matched_nodes:
            raise NodeDoesNotExistError(error_code=1763729190, aruco_id=aruco_id)
        values = next(iter(matched_nodes.values()))
        return values

    def getOPCUANodeByID(self, aruco_id: Optional[int] = None) -> Optional[str]:
        matched_node = self._findNodeByID(aruco_id=aruco_id)
        return matched_node[SENSOR_KEYS.OPCUA_NODE]

    def getScoreFunctionStr(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Optional[str]:
        matched_node = self._findNodeByID(
            aruco_id=aruco_id, allow_missing=allow_missing
        )
        return matched_node.get(SENSOR_KEYS.SCORE_FUNCTION)

    def getScoreFunction(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Optional[Callable[[float], float]]:

        score_function_str = self.getScoreFunctionStr(
            aruco_id=aruco_id, allow_missing=allow_missing
        )
        parameters = self.getParameters(aruco_id=aruco_id, allow_missing=allow_missing)

        return lambda x: eval(
            score_function_str, {"exp": math.exp, "pow": math.pow, **parameters, "x": x}
        )

    def getParameters(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Optional[dict]:
        matched_node = self._findNodeByID(
            aruco_id=aruco_id, allow_missing=allow_missing
        )

        if matched_node.get(SENSOR_KEYS.PARAMETERS) is None:
            return {}

        return matched_node.get(SENSOR_KEYS.PARAMETERS)

    def getRiskManagement(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> dict:
        matched_node = self._findNodeByID(
            aruco_id=aruco_id, allow_missing=allow_missing
        )
        return matched_node.get(SENSOR_KEYS.RISK_MANAGEMENT)

    def getSafeRange(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Optional[float]:
        return self.getRiskManagement(
            aruco_id=aruco_id, allow_missing=allow_missing
        ).get(SENSOR_KEYS.SAFE_RANGE)

    def getUncertainRange(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Optional[float]:
        return self.getRiskManagement(
            aruco_id=aruco_id, allow_missing=allow_missing
        ).get(SENSOR_KEYS.UNCERTAIN_RANGE)

    def getAnomalyRange(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Optional[float]:
        return self.getRiskManagement(
            aruco_id=aruco_id, allow_missing=allow_missing
        ).get(SENSOR_KEYS.ANOMALY_RANGE)

    def getMinMaxValue(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Optional[Tuple[float, float]]:
        parameters = self.getParameters(aruco_id=aruco_id, allow_missing=allow_missing)

        min_value = parameters.get(SENSOR_KEYS.PARAMETERS_MIN_VALUE)
        max_value = parameters.get(SENSOR_KEYS.PARAMETERS_MAX_VALUE)

        if min_value > max_value:
            raise MinMaxValueError(
                error_code=1764624580,
                id=aruco_id,
                min_value=min_value,
                max_value=max_value,
            )

        return (
            parameters.get(SENSOR_KEYS.PARAMETERS_MIN_VALUE),
            parameters.get(SENSOR_KEYS.PARAMETERS_MAX_VALUE),
        )

    def getMinMaxAngle(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Optional[Tuple[float, float]]:
        matched_node = self._findNodeByID(
            aruco_id=aruco_id, allow_missing=allow_missing
        )
        return (
            matched_node.get(SENSOR_KEYS.MIN_ANGLE),
            matched_node.get(SENSOR_KEYS.MAX_ANGLE),
        )

    def getUnit(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Optional[str]:
        matched_node = self._findNodeByID(
            aruco_id=aruco_id, allow_missing=allow_missing
        )
        return matched_node.get(SENSOR_KEYS.UNIT)
