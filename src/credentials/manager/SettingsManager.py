from common.imports.Typing import Any, Optional, Callable, Tuple, List, Dict

from credentials.configs.reader.MinioBucketConfigReader import MinioBucketConfigReader
from credentials.configs.reader.SensorConfigReader import SensorConfigReader


class SettingsManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        minio_bucket_reader: Optional[MinioBucketConfigReader] = None,
        sensor_config_reader: Optional[SensorConfigReader] = None,
    ):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._initialized = True
        self._minio_bucket_reader = minio_bucket_reader or MinioBucketConfigReader()
        self._sensor_config_reader = sensor_config_reader or SensorConfigReader()

    def getMinioRawBucket(self) -> Optional[str]:
        return self._minio_bucket_reader.getRawBucket()

    def getMinioAnalyzedBucket(self) -> Optional[str]:
        return self._minio_bucket_reader.getAnalyzedBucket()

    def getArUcoOverallDict(self) -> dict:
        return self._sensor_config_reader.getOverallDict()

    def getOPCUANodeByID(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[str]:
        return self._sensor_config_reader.getOPCUANodeByID(
            aruco_id=aruco_id, category_name=category_name
        )

    def getCategoriesNameByNodeID(self, aruco_id: int) -> List[str]:
        return self._sensor_config_reader.getCategoriesNameByNodeID(aruco_id=aruco_id)

    def getCategoryByCategoryNameAndArucoID(
        self, category_name: str, aruco_id: int
    ) -> Dict[str, Any]:
        return self._sensor_config_reader.getCategoryByCategoryNameAndArucoID(
            category_name=category_name, aruco_id=aruco_id
        )

    def getScoreFunctionStr(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[str]:
        return self._sensor_config_reader.getScoreFunctionStr(
            aruco_id=aruco_id, category_name=category_name
        )

    def getScoreFunction(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[Callable[[float], float]]:
        return self._sensor_config_reader.getScoreFunction(
            aruco_id=aruco_id, category_name=category_name
        )

    def getSafeRange(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[float]:
        return self._sensor_config_reader.getSafeRange(
            aruco_id=aruco_id, category_name=category_name
        )

    def getUncertainRange(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[float]:
        return self._sensor_config_reader.getUncertainRange(
            aruco_id=aruco_id, category_name=category_name
        )

    def getAnomalyRange(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[float]:
        return self._sensor_config_reader.getAnomalyRange(
            aruco_id=aruco_id, category_name=category_name
        )

    def getMinMaxValue(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[Tuple[float, float]]:
        return self._sensor_config_reader.getMinMaxValue(
            aruco_id=aruco_id, category_name=category_name
        )

    def getParametersForAnomalyMapper(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[dict[str, Any]]:
        parameters = self._sensor_config_reader.getParameters(
            aruco_id=aruco_id, category_name=category_name
        )
        risk_management = self._sensor_config_reader.getRiskManagement(
            aruco_id=aruco_id, category_name=category_name
        )
        return {**parameters, **risk_management}

    def getUnit(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[str]:
        return self._sensor_config_reader.getUnit(
            aruco_id=aruco_id, category_name=category_name
        )

    def getValueTolerance(
        self, category_name: str, aruco_id: Optional[int] = None
    ) -> Optional[float]:
        return self._sensor_config_reader.getValueTolerance(
            aruco_id=aruco_id, category_name=category_name
        )
