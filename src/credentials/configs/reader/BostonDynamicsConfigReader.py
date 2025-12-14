from common.imports.Typing import Optional
from credentials.configs.loader.ConfigLoader import ConfigLoader
from credentials.configs.enum.ConfigEnum import ConfigEnum, ROBOT_KEYS


class BostonDynamicsConfigReader(ConfigLoader):
    def __init__(self):
        super().__init__()
        self.__config = self.load_config(ConfigEnum.ROBOT_CONFIG)

    def _getRobot(self) -> dict:
        value = self.__config.get(ROBOT_KEYS.ROBOT)
        if not isinstance(value, dict):
            return {}
        return value

    def getIP(self) -> Optional[str]:
        return self._getRobot().get(ROBOT_KEYS.IP)

    def getWifi(self) -> Optional[str]:
        return self._getRobot().get(ROBOT_KEYS.WIFI)

    def getUser(self) -> Optional[str]:
        return self._getRobot().get(ROBOT_KEYS.USER)
