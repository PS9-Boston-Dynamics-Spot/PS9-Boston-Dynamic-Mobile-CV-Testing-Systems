from enum import Enum


class EnvEnum(str, Enum):
    """
    Enthält die Pfade zu deinen .env-Dateien.
    Im einfachsten Fall relativ zum Projektroot.
    """

    MINIO_ENV = ".env/minio-credentials.env"
    ROBOT_ENV = ".env/robot-credentials.env"

    def __str__(self) -> str:
        return self.value
