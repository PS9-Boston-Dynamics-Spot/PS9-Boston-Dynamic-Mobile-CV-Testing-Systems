from enum import Enum

class MINIO_KEYS(str, Enum):
    SECRET_KEY = "SECRET_KEY"

    def __str__(self) -> str:
        return self.value



class ROBOT_KEYS(str, Enum):
    PASSWORD = "PASSWORD"

    def __str__(self) -> str:
        return self.value



class EnvEnum(str, Enum):
    MINIO_ENV = ".env/minio-credentials.env"
    ROBOT_ENV = ".env/robot-credentials.env"

    def __str__(self) -> str:
        return self.value
