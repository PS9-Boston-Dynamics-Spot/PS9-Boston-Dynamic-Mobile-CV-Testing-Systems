from typing import Dict, Any, Optional

from configs.reader.MinioConfigReader import MinioConfigReader
from configs.reader.MinioBucketConfigReader import MinioBucketConfigReader
from configs.reader.SqliteConfigReader import SqliteConfigReader
from configs.reader.BostonDynamicsConfigReader import BostonDynamicsConfigReader
from configs.reader.env_reader import EnvReader


class UnifiedConfigManager:
    """
    Zentrale Klasse, die alle Config- und Env-Zugriffe bündelt.
    Gibt für MinIO, Robot, DB jeweils ein fertiges Dict zurück.

    Wichtig:
    - YAML-Dateien werden über deine bestehenden *ConfigReader geladen.
    - .env-Dateien über EnvReader.
    - Die Loader öffnen Dateien immer nur kurz und schließen sie sofort.
    """

    def __init__(
        self,
        minio_config_reader: Optional[MinioConfigReader] = None,
        minio_bucket_reader: Optional[MinioBucketConfigReader] = None,
        sqlite_config_reader: Optional[SqliteConfigReader] = None,
        robot_config_reader: Optional[BostonDynamicsConfigReader] = None,
        env_reader: Optional[EnvReader] = None,
    ) -> None:
        self._minio_config_reader = minio_config_reader or MinioConfigReader()
        self._minio_bucket_reader = minio_bucket_reader or MinioBucketConfigReader()
        self._sqlite_config_reader = sqlite_config_reader or SqliteConfigReader()
        self._robot_config_reader = robot_config_reader or BostonDynamicsConfigReader()
        self._env_reader = env_reader or EnvReader()

    # -------------------------------------------------------------------------
    # MinIO
    # -------------------------------------------------------------------------
    def getMinioCreds(self) -> Dict[str, Any]:
        """
        Kombiniert:
        - host, port, tls (YAML über MinioConfigReader)
        - access_key, secret_key (aus .env über EnvReader;
          Fallback: Werte aus YAML, solange sie dort noch existieren)
        - raw_bucket, analyzed_bucket (YAML über MinioBucketConfigReader)
        """
        host = self._minio_config_reader.getHost()
        port = self._minio_config_reader.getPort()
        tls = self._minio_config_reader.getTls()

        # Env zuerst, YAML als Fallback -> sanfte Migration
        access_key = self._env_reader.getMinioAccessKey() or \
            self._minio_config_reader.getAccessKey()
        secret_key = self._env_reader.getMinioSecretKey() or \
            self._minio_config_reader.getSecretKey()

        raw_bucket = self._minio_bucket_reader.getRawBucket()
        analyzed_bucket = self._minio_bucket_reader.getAnalyzedBucket()

        return {
            "host": host,
            "port": port,
            "tls": tls,
            "access_key": access_key,
            "secret_key": secret_key,
            "raw_bucket": raw_bucket,
            "analyzed_bucket": analyzed_bucket,
        }

    # -------------------------------------------------------------------------
    # SQLite
    # -------------------------------------------------------------------------
    def getDBCreds(self) -> Dict[str, Any]:
        """
        Alles aus SQLite-Config (YAML).
        Falls später User/Pass sensibel werden, können die auch in .env landen.
        """
        return {
            "database": self._sqlite_config_reader.getDatabase(),
            "timeout": self._sqlite_config_reader.getTimeout(),
            "detect_types": self._sqlite_config_reader.getDetectTypes(),
            "isolation_level": self._sqlite_config_reader.getIsolationLevel(),
            "check_same_thread": self._sqlite_config_reader.getCheckSameThread(),
            "cached_statements": self._sqlite_config_reader.getCachedStatements(),
            "uri": self._sqlite_config_reader.getUri(),
        }

    # -------------------------------------------------------------------------
    # Boston Dynamics Robot
    # -------------------------------------------------------------------------
    def getRobotCreds(self) -> Dict[str, Any]:
        """
        Kombiniert:
        - ip, wifi, user (YAML)
        - password (aus .env, Fallback: YAML)
        """
        ip = self._robot_config_reader.getIP()
        wifi = self._robot_config_reader.getWifi()
        user = self._robot_config_reader.getUser()
        password = self._env_reader.getRobotPassword() or \
            self._robot_config_reader.getPassword()

        return {
            "ip": ip,
            "wifi": wifi,
            "user": user,
            "password": password,
        }
