from common.imports.Typing import Any, Optional, Callable, Tuple, List

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
        self._sensor_config_reader = (
            sensor_config_reader or SensorConfigReader()
        )

    def getMinioRawBucket(self) -> Optional[str]:
        return self._minio_bucket_reader.getRawBucket()

    def getMinioAnalyzedBucket(self) -> Optional[str]:
        return self._minio_bucket_reader.getAnalyzedBucket()
    




    def getArUcoOverallDict(self) -> dict:
        return self._sensor_config_reader.getOverallDict()

    def getOPCUANodeByID(self, aruco_id: Optional[int] = None) -> Optional[str]:
        return self._sensor_config_reader.getOPCUANodeByID(aruco_id=aruco_id)
    
    def getCategoriesNameByNodeID(self, aruco_id: int) -> List[str]:
        return self._sensor_config_reader.getCategoriesNameByNodeID(aruco_id=aruco_id)

    def getScoreFunctionStr(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Optional[str]:
        return self._sensor_config_reader.getScoreFunctionStr(
            aruco_id=aruco_id, allow_missing=allow_missing
        )

    def getScoreFunction(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Optional[Callable[[float], float]]:
        return self._sensor_config_reader.getScoreFunction(
            aruco_id=aruco_id, allow_missing=allow_missing
        )

    def getSafeRange(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Optional[float]:
        return self._sensor_config_reader.getSafeRange(
            aruco_id=aruco_id, allow_missing=allow_missing
        )

    def getUncertainRange(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Optional[float]:
        return self._sensor_config_reader.getUncertainRange(
            aruco_id=aruco_id, allow_missing=allow_missing
        )

    def getAnomalyRange(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Optional[float]:
        return self._sensor_config_reader.getAnomalyRange(
            aruco_id=aruco_id, allow_missing=allow_missing
        )

    def getMinMaxValue(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Optional[Tuple[float, float]]:
        return self._sensor_config_reader.getMinMaxValue(
            aruco_id=aruco_id, allow_missing=allow_missing
        )

    def getParametersForAnomalyMapper(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Optional[dict[str, Any]]:
        parameters = self._sensor_config_reader.getParameters(
            aruco_id=aruco_id, allow_missing=allow_missing
        )
        risk_management = self._sensor_config_reader.getRiskManagement(
            aruco_id=aruco_id, allow_missing=allow_missing
        )
        return {**parameters, **risk_management}

    def getMinMaxAngle(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Optional[Tuple[float, float]]:
        return self._sensor_config_reader.getMinMaxAngle(
            aruco_id=aruco_id, allow_missing=allow_missing
        )

    def getUnit(
        self, aruco_id: Optional[int] = None, allow_missing: bool = False
    ) -> Optional[str]:
        return self._sensor_config_reader.getUnit(
            aruco_id=aruco_id, allow_missing=allow_missing
        )
