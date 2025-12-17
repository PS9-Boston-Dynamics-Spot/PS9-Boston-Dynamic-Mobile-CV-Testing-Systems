from common.imports.Typing import Optional, Dict, Any, Callable, Tuple, List
import math
from credentials.configs.loader.ConfigLoader import ConfigLoader
from credentials.configs.enum.ConfigEnum import ConfigEnum, SENSOR_KEYS
from credentials.configs.exceptions.MultipleIDsError import MultipleIDsError
from credentials.configs.exceptions.NodeDoesNotExistError import NodeDoesNotExistError
from credentials.configs.exceptions.MinMaxValueError import MinMaxValueError
from credentials.configs.exceptions.CategoryDoesNotExistError import CategoryDoesNotExistError


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
        self, aruco_id: Optional[int] = None
    ) -> Dict[str, Dict[str, Any]]:
        nodes = self._getNodes()
        matched_nodes: Dict[str, Dict[str, Any]] = {}

        for node_name, props in nodes.items():
            node_aruco_id = props[SENSOR_KEYS.ARUCO_ID]            
            if node_aruco_id == aruco_id:
                matched_nodes[node_name] = props

        if len(matched_nodes) > 1:
            raise MultipleIDsError(
                error_code=1763491580, nodes=list(matched_nodes.keys()), id=aruco_id
            )

        if not matched_nodes:
            raise NodeDoesNotExistError(error_code=1763729190, aruco_id=aruco_id)
        
        values = next(iter(matched_nodes.values()))
        return values
    
    def getCategoriesNameByNodeID(self, aruco_id: int) -> List[str]:
        matched_node = self._findNodeByID(aruco_id=aruco_id)
        categories = matched_node.get(SENSOR_KEYS.CATEGORIES, [])
        return [category[SENSOR_KEYS.NAME] for category in categories]
    
    def getCategoryByCategoryNameAndArucoID(self, category_name: str, aruco_id: int) -> Dict[str, Any]:
        matched_node = self._findNodeByID(aruco_id=aruco_id)
        categories = matched_node.get(SENSOR_KEYS.CATEGORIES, [])
        
        for category in categories:
            if category[SENSOR_KEYS.NAME] == category_name:
                return category
        
        raise CategoryDoesNotExistError(error_code=1765983500, category_name=category_name, aruco_id=aruco_id)



    def getOPCUANodeByID(self, category_name: str, aruco_id: Optional[int] = None, ) -> Optional[str]:
        matched_node = self.getCategoryByCategoryNameAndArucoID(aruco_id=aruco_id, category_name=category_name)
        return matched_node[SENSOR_KEYS.OPCUA_NODE]
    
    def getValueTolerance(self, category_name: str, aruco_id: Optional[int] = None) -> Optional[float]:
        matched_node = self.getCategoryByCategoryNameAndArucoID(aruco_id=aruco_id, category_name=category_name)
        return matched_node.get(SENSOR_KEYS.VALUE_TOLERANCE)

    def getScoreFunctionStr(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[str]:
        matched_node = self.getCategoryByCategoryNameAndArucoID(
            aruco_id=aruco_id, category_name=category_name
        )
        return matched_node.get(SENSOR_KEYS.SCORE_FUNCTION)

    def getScoreFunction(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[Callable[[float], float]]:

        score_function_str = self.getScoreFunctionStr(
            aruco_id=aruco_id, category_name=category_name
        )
        parameters = self.getParameters(aruco_id=aruco_id, category_name=category_name)

        return lambda x: eval(
            score_function_str, {"exp": math.exp, "pow": math.pow, **parameters, "x": x}
        )

    def getParameters(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[dict]:
        matched_node = self.getCategoryByCategoryNameAndArucoID(
            aruco_id=aruco_id, category_name=category_name
        )

        if matched_node.get(SENSOR_KEYS.PARAMETERS) is None:
            return {}

        return matched_node.get(SENSOR_KEYS.PARAMETERS)

    def getRiskManagement(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> dict:
        matched_node = self.getCategoryByCategoryNameAndArucoID(
            aruco_id=aruco_id, category_name=category_name
        )
        return matched_node.get(SENSOR_KEYS.RISK_MANAGEMENT)

    def getSafeRange(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[float]:
        return self.getRiskManagement(
            aruco_id=aruco_id, category_name=category_name
        ).get(SENSOR_KEYS.SAFE_RANGE)

    def getUncertainRange(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[float]:
        return self.getRiskManagement(
            aruco_id=aruco_id, category_name=category_name
        ).get(SENSOR_KEYS.UNCERTAIN_RANGE)

    def getAnomalyRange(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[float]:
        return self.getRiskManagement(
            aruco_id=aruco_id, category_name=category_name
        ).get(SENSOR_KEYS.ANOMALY_RANGE)

    def getMinMaxValue(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[Tuple[float, float]]:
        parameters = self.getParameters(aruco_id=aruco_id, category_name=category_name)

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
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[Tuple[float, float]]:
        matched_node = self.getCategoryByCategoryNameAndArucoID(
            aruco_id=aruco_id, category_name=category_name
        )
        return (
            matched_node.get(SENSOR_KEYS.MIN_ANGLE),
            matched_node.get(SENSOR_KEYS.MAX_ANGLE),
        )

    def getUnit(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[str]:
        matched_node = self.getCategoryByCategoryNameAndArucoID(
            aruco_id=aruco_id, category_name=category_name
        )
        return matched_node.get(SENSOR_KEYS.UNIT)
