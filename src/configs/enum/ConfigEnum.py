from enum import Enum

class MINIO_KEYS(str, Enum):
    MINIO = "minio"
    HOST = "host"
    PORT = "port"
    ACCESS_KEY = "access_key"
    SECRET_KEY = "secret_key" # TODO: outsource into .env
    TLS = "tls"

class ROBOT_KEYS(str, Enum):
    ROBOT = "robot"
    IP = "ip"
    WIFI = "wifi"
    USER = "user"
    PASSWORD = "password" # TODO: outsource into .env

class ConfigEnum(str, Enum):
    CONFIG_DIR = "configs/"
    ROBOT_CONFIG = CONFIG_DIR + "robot-credentials.yaml"
    MINIO_CONFIG = CONFIG_DIR + "minio-credentials.yaml"

    def __str__(self) -> str:
        return self.value
