from credentials.env.loader.EnvLoader import EnvLoader
from credentials.env.enum.EnvEnum import EnvEnum, ROBOT_KEYS
from common.imports.Typing import Optional


class RobotEnvReader(EnvLoader):
    def __init__(self):
        super().__init__()
        self.__robot_env = self.load_env(EnvEnum.ROBOT_ENV)

    def getRobotPassword(self) -> Optional[str]:
        return self.__robot_env.get(ROBOT_KEYS.PASSWORD)
