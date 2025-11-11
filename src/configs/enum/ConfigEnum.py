from enum import Enum


class OPCUA_NODES(str, Enum):
    NODES = "nodes"
    OVEN_NODE = "oven_node"


class MINIO_BUCKETS(str, Enum):
    BUCKETS = "buckets"
    RAW_BUCKET = "raw_bucket"
    ANALYZED_BUCKET = "analyzed_bucket"


class OPCUA_KEYS(str, Enum):
    OPCUA = "opcua"
    IP = "ip"
    PORT = "port"
    PROTOCOL = "protocol"
    TIMEOUT = "timeout"


class SQLITE_KEYS(str, Enum):
    SQLITE = "sqlite"
    DATABASE = "database"
    TIMEOUT = "timeout"
    DETECT_TYPES = "detect_types"
    ISOLATION_LEVEL = "isolation_level"
    CHECK_SAME_THREAD = "check_same_thread"
    CACHED_STATEMENTS = "cached_statements"
    URI = "uri"


class MINIO_KEYS(str, Enum):
    MINIO = "minio"
    HOST = "host"
    PORT = "port"
    ACCESS_KEY = "access_key"
    SECRET_KEY = "secret_key"  # TODO: outsource into .env
    TLS = "tls"


class ROBOT_KEYS(str, Enum):
    ROBOT = "robot"
    IP = "ip"
    WIFI = "wifi"
    USER = "user"
    PASSWORD = "password"  # TODO: outsource into .env


class ConfigEnum(str, Enum):
    WORKSPACE_DIR = "/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/"
    CONFIG_DIR = WORKSPACE_DIR + "configs/"
    ROBOT_CONFIG = CONFIG_DIR + "robot-credentials.yaml"
    MINIO_CONFIG = CONFIG_DIR + "minio-credentials.yaml"
    SQLITE_CONFIG = CONFIG_DIR + "sqlite-credentials.yaml"
    BUCKETS_CONFIG = CONFIG_DIR + "minio-buckets.yaml"
    OPCUA_CONFIG = CONFIG_DIR + "opcua-credentials.yaml"
    OPCUA_NODES_CONFIG = CONFIG_DIR + "opcua-nodes.yaml"

    def __str__(self) -> str:
        return self.value
