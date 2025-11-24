from typing import Any, Optional

from credentials.configs.reader.MinioConfigReader import MinioConfigReader
from credentials.configs.reader.MinioBucketConfigReader import MinioBucketConfigReader
from credentials.configs.reader.SqliteConfigReader import SqliteConfigReader
from credentials.configs.reader.BostonDynamicsConfigReader import BostonDynamicsConfigReader
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
        self._minio_env_reader = minio_env_reader or MinioEnvReader()
        self._robot_env_reader = robot_env_reader or RobotEnvReader()

    def getMinioCredentials(self) -> dict[str, Any]:
        host = self._minio_config_reader.getHost()
        port = self._minio_config_reader.getPort()
        tls = self._minio_config_reader.getTls()

        access_key = self._minio_config_reader.getAccessKey()
        secret_key = self._minio_env_reader.getMinioSecretKey()

        return {
            "host": host,
            "port": port,
            "tls": tls,
            "access_key": access_key,
            "secret_key": secret_key,
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
        ip = self._robot_config_reader.getIP()
        wifi = self._robot_config_reader.getWifi()
        user = self._robot_config_reader.getUser()
        password = self._robot_env_reader.getRobotPassword()

        return {
            "ip": ip,
            "wifi": wifi,
            "user": user,
            "password": password,
        }