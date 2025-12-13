from typing import Optional, Dict, Any, Callable, Tuple
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

    def _getAnalogGauge(self) -> dict:
        value = self.__config.get(SENSOR_KEYS.ANALOG_GAUGE)
        if not isinstance(value, dict):
            return {}
        return value

    def getAnalogGaugeMinAngle(self) -> Optional[float]:
        return self._getAnalogGauge().get(SENSOR_KEYS.MIN_ANGLE)

    def getAnalogGaugeMaxAngle(self) -> Optional[float]:
        return self._getAnalogGauge().get(SENSOR_KEYS.MAX_ANGLE)

    def getAnalogGaugeMinValue(self) -> Optional[float]:
        return self._getAnalogGauge().get(SENSOR_KEYS.ANALOG_GAUGE_MIN_VALUE)

    def getAnalogGaugeMaxValue(self) -> Optional[float]:
        return self._getAnalogGauge().get(SENSOR_KEYS.ANALOG_GAUGE_MAX_VALUE)

    def getAnalogGaugeUnit(self) -> Optional[str]:
        return self._getAnalogGauge().get(SENSOR_KEYS.UNIT)

    def _getNodes(self) -> dict:
        value = self.__config.get(SENSOR_KEYS.NODES)
        if not isinstance(value, dict):
            return {}
        return value

    def _findNodeByID(self, aruco_id: int) -> Dict[str, Dict[str, Any]]:
        nodes = self._getNodes()

        matched_nodes: Dict[str, Dict[str, Any]] = {}

        for node_name, props in nodes.items():
            if props.get(SENSOR_KEYS.ARUCO_ID) == aruco_id:
                matched_nodes[node_name] = props

        if len(matched_nodes) > 1:
            raise MultipleIDsError(
                error_code=1763491580, nodes=list(matched_nodes.keys()), id=aruco_id
            )

        if len(matched_nodes) < 1:
            raise NodeDoesNotExistError(error_code=1763729190, aruco_id=aruco_id)

        node_props = next(iter(matched_nodes.values()))
        return node_props

    def getOPCUANodeByID(self, aruco_id: int) -> Optional[str]:
        matched_node = self._findNodeByID(aruco_id=aruco_id)
        return matched_node[SENSOR_KEYS.OPCUA_NODE]

    def getScoreFunctionStr(self, aruco_id: int) -> Optional[str]:
        matched_node = self._findNodeByID(aruco_id=aruco_id)
        return matched_node.get(SENSOR_KEYS.SCORE_FUNCTION)

    def getScoreFunction(self, aruco_id: int) -> Optional[Callable[[float], float]]:

        score_function_str = self.getScoreFunctionStr(aruco_id=aruco_id)
        parameters = self.getParameters(aruco_id=aruco_id)

        return lambda x: eval(
            score_function_str, {"exp": math.exp, "pow": math.pow, **parameters, "x": x}
        )

    def getParameters(self, aruco_id: int) -> Optional[dict]:
        matched_node = self._findNodeByID(aruco_id=aruco_id)

        if matched_node.get(SENSOR_KEYS.PARAMETERS) is None:
            return {}

        min_value, max_value = self.getMinMaxValue(aruco_id=aruco_id)

        if min_value > max_value:
            raise MinMaxValueError(
                error_code=1764624580,
                node=matched_node.get(SENSOR_KEYS.OPCUA_NODE),
                id=aruco_id,
                min_value=min_value,
                max_value=max_value,
            )

        return matched_node.get(SENSOR_KEYS.PARAMETERS)

    def getRiskManagement(self, aruco_id: int) -> dict:
        matched_node = self._findNodeByID(aruco_id=aruco_id)
        return matched_node.get(SENSOR_KEYS.RISK_MANAGEMENT)

    def getSafeRange(self, aruco_id: int) -> Optional[float]:
        return self.getRiskManagement(aruco_id=aruco_id).get(SENSOR_KEYS.SAFE_RANGE)

    def getUncertainRange(self, aruco_id: int) -> Optional[float]:
        return self.getRiskManagement(aruco_id=aruco_id).get(
            SENSOR_KEYS.UNCERTAIN_RANGE
        )

    def getAnomalyRange(self, aruco_id: int) -> Optional[float]:
        return self.getRiskManagement(aruco_id=aruco_id).get(SENSOR_KEYS.ANOMALY_RANGE)

    def getMinMaxValue(self, aruco_id: int) -> Optional[Tuple[float, float]]:
        matched_node = self.getParameters(aruco_id=aruco_id)
        return (
            matched_node.get(SENSOR_KEYS.PARAMETERS_MIN_VALUE),
            matched_node.get(SENSOR_KEYS.PARAMETERS_MAX_VALUE),
        )
