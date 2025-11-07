from enum import Enum


class ROBOT_KEYS(str, Enum):
    ROBOT = "robot"
    IP = "ip"
    WIFI = "wifi"
    USER = "user"
    PASSWORD = "password"


class ConfigEnum(str, Enum):
    ROBOT = "configs/robot-credentials.yaml"

    def __str__(self) -> str:
        return self.value
