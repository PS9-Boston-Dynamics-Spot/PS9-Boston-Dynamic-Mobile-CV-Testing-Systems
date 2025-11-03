from typing import Optional
from configs.loader.ConfigLoader import ConfigLoader
from configs.enum.ConfigEnum import ConfigEnum, MINIO_KEYS


class MinioConfigReader(ConfigLoader):
    def __init__(self):
        super().__init__()
        self.__config = self.load_config(ConfigEnum.MINIO_CONFIG)

    def _getMinio(self) -> dict:
        value = self.__config.get(MINIO_KEYS.MINIO)
        if not isinstance(value, dict):
            return {}
        return value

    def getHost(self) -> Optional[str]:
        return self._getMinio().get(MINIO_KEYS.HOST)

    def getPort(self) -> Optional[str]:
        return self._getMinio().get(MINIO_KEYS.PORT)

    def getAccessKey(self) -> Optional[str]:
        return self._getMinio().get(MINIO_KEYS.ACCESS_KEY)

    def getSecretKey(self) -> Optional[str]:
        return self._getMinio().get(
            MINIO_KEYS.SECRET_KEY
        )  # TODO: outsource into a .env file

    def getTls(self) -> Optional[bool]:
        return self._getMinio().get(MINIO_KEYS.TLS)
