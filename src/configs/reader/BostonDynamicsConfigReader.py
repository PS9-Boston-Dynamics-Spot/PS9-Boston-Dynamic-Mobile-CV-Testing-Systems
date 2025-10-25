from typing import Dict, Any, Optional
from configs.loader.ConfigLoader import ConfigLoader
from configs.enum.ConfigEnum import ConfigEnum, ROBOT_KEYS


class BostonDynamicsConfigReader(ConfigLoader):
    def __init__(self):
        super().__init__()
        self.__config = self.load_config(ConfigEnum.ROBOT_CONFIG)

    def _getRobot(self) -> Dict[str, Any]:
        return self.__config.get(ROBOT_KEYS.ROBOT, {})

    def getIP(self) -> Optional[str]:
        return self._getRobot().get(ROBOT_KEYS.IP)

    def getWifi(self) -> Optional[str]:
        return self._getRobot().get(ROBOT_KEYS.WIFI)

    def getUser(self) -> Optional[str]:
        return self._getRobot().get(ROBOT_KEYS.USER)

    def getPassword(self) -> Optional[str]:
        return self._getRobot().get(
            ROBOT_KEYS.PASSWORD
        )  # TODO: outsource into a .env file (e.g. .env/robot-credentials.env)
