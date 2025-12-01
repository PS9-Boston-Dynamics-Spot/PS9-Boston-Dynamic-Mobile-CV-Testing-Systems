from typing import Any, Optional, Callable

from credentials.configs.reader.MinioConfigReader import MinioConfigReader
from credentials.configs.reader.MinioBucketConfigReader import MinioBucketConfigReader
from credentials.configs.reader.SqliteConfigReader import SqliteConfigReader
from credentials.configs.reader.BostonDynamicsConfigReader import BostonDynamicsConfigReader
from credentials.configs.reader.OPCUAConfigReader import OPCUAConfigReader
from credentials.configs.reader.OPCUANodesConfigReader import OPCUANodesConfigReader
from credentials.env.reader.MinioEnvReader import MinioEnvReader
from credentials.env.reader.RobotEnvReader import RobotEnvReader


class UnifiedCredentialsManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        minio_config_reader: Optional[MinioConfigReader] = None,
        minio_bucket_reader: Optional[MinioBucketConfigReader] = None,
        sqlite_config_reader: Optional[SqliteConfigReader] = None,
        robot_config_reader: Optional[BostonDynamicsConfigReader] = None,
        opcua_config_reader: Optional[OPCUAConfigReader] = None,
        opcua_nodes_config_reader: Optional[OPCUANodesConfigReader] = None,
        minio_env_reader: Optional[MinioEnvReader] = None,
        robot_env_reader: Optional[RobotEnvReader] = None
    ):
        if hasattr(self, "_initialized") and self._initialized:
            return

        print("test")

        self._initialized = True

        self._minio_config_reader = minio_config_reader or MinioConfigReader()
        self._minio_bucket_reader = minio_bucket_reader or MinioBucketConfigReader()
        self._sqlite_config_reader = sqlite_config_reader or SqliteConfigReader()
        self._robot_config_reader = robot_config_reader or BostonDynamicsConfigReader()
        self._opcua_config_reader = opcua_config_reader or OPCUAConfigReader()
        self._opcua_nodes_config_reader = opcua_nodes_config_reader or OPCUANodesConfigReader()
        self._minio_env_reader = minio_env_reader or MinioEnvReader()
        self._robot_env_reader = robot_env_reader or RobotEnvReader()

    def getMinioCredentials(self) -> dict[str, Any]:
        return {
            "host": self._minio_config_reader.getHost(),
            "port": self._minio_config_reader.getPort(),
            "tls": self._minio_config_reader.getTls(),
            "access_key": self._minio_config_reader.getAccessKey(),
            "secret_key": self._minio_env_reader.getMinioSecretKey(),
        }
    
    def getMinioRawBucket(self) -> Optional[str]:
        return self._minio_bucket_reader.getRawBucket()
    
    def getMinioAnalyzedBucket(self) -> Optional[str]:
        return self._minio_bucket_reader.getAnalyzedBucket()

    def getDBCredentials(self) -> dict[str, Any]:
        return {
            "database": self._sqlite_config_reader.getDatabase(),
            "timeout": self._sqlite_config_reader.getTimeout(),
            "detect_types": self._sqlite_config_reader.getDetectTypes(),
            "isolation_level": self._sqlite_config_reader.getIsolationLevel(),
            "check_same_thread": self._sqlite_config_reader.getCheckSameThread(),
            "cached_statements": self._sqlite_config_reader.getCachedStatements(),
            "uri": self._sqlite_config_reader.getUri(),
        }

    def getRobotCredentials(self) -> dict[str, Any]:
        return {
            "ip": self._robot_config_reader.getIP(),
            "wifi": self._robot_config_reader.getWifi(),
            "user": self._robot_config_reader.getUser(),
            "password": self._robot_env_reader.getRobotPassword(),
        }
    
    def getOPCUACredentials(self) -> dict[str, Any]:
        return {
            "ip": self._opcua_config_reader.getIp(),
            "port": self._opcua_config_reader.getPort(),
            "protocol": self._opcua_config_reader.getProtocol(),
            "timeout": self._opcua_config_reader.getTimeout(),
        }
    
    def getArUcoOverallDict(self) -> dict:
        return self._opcua_nodes_config_reader.getOverallDict()
    
    def getOPCUANodeByID(self, aruco_id: int) -> dict[str, Any]:
        return self._opcua_nodes_config_reader.getOPCUANodeByID(aruco_id=aruco_id)

    def getScoreFunction(self, aruco_id: int) -> Optional[Callable[[float], float]]:
        return self._opcua_nodes_config_reader.getScoreFunction(aruco_id=aruco_id)
    
    def getParameters(self, aruco_id: int) -> Optional[dict]:
        return self._opcua_nodes_config_reader.getParameters(aruco_id=aruco_id)
    
    def getSafeRange(self, aruco_id: int) -> Optional[float]:
        return self._opcua_nodes_config_reader.getSafeRange(aruco_id=aruco_id)
    
    def getUncertainRange(self, aruco_id: int) -> Optional[float]:
        return self._opcua_nodes_config_reader.getUncertainRange(aruco_id=aruco_id)
    
    def getAnomalyRange(self, aruco_id: int) -> Optional[float]:
        return self._opcua_nodes_config_reader.getAnomalyRange(aruco_id=aruco_id)