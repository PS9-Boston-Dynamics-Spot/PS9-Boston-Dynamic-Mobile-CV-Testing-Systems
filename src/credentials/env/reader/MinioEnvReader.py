from typing import Optional

from credentials.env.loader.EnvLoader import EnvLoader
from credentials.env.enum.EnvEnum import EnvEnum, MINIO_KEYS


class MinioEnvReader(EnvLoader):
    def __init__(self):
        super().__init__()
        self.__minio_env = self.load_env(EnvEnum.MINIO_ENV)

    def getMinioSecretKey(self) -> Optional[str]:
        return self.__minio_env.get(MINIO_KEYS.SECRET_KEY)
