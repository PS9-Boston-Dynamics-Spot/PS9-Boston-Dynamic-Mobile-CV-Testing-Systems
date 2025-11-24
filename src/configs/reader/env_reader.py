from typing import Optional, Dict

from configs.loader.env_loader import EnvLoader
from configs.enum.env_enum import EnvEnum


class EnvReader(EnvLoader):
    def __init__(self) -> None:
        super().__init__()
        # jeweils einmal lesen, Datei ist danach zu
        self.__minio_env: Dict[str, str] = self.load_env(EnvEnum.MINIO_ENV)
        self.__robot_env: Dict[str, str] = self.load_env(EnvEnum.ROBOT_ENV)

    # ---------- MinIO ----------
    def getMinioAccessKey(self) -> Optional[str]:
        return self.__minio_env.get("MINIO_ACCESS_KEY")

    def getMinioSecretKey(self) -> Optional[str]:
        return self.__minio_env.get("MINIO_SECRET_KEY")

    # ---------- Robot ----------
    def getRobotPassword(self) -> Optional[str]:
        return self.__robot_env.get("ROBOT_PASSWORD")


