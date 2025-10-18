from typing import Dict, Any, Optional
from common.utils.ConfigLoader import ConfigLoader
from common.utils.ConfigEnum import ConfigEnum, ROBOT_KEYS

class BostonDynamicsConfigLoader(ConfigLoader):
    def __init__(self):
        super().__init__()
        self.__config = self.load_config(ConfigEnum.ROBOT)

    def _get_robot(self) -> Dict[str, Any]:
        return self.__config.get(ROBOT_KEYS.ROBOT, {})

    def getIP(self) -> Optional[str]:
        return self._get_robot().get(ROBOT_KEYS.IP)

    def getWifi(self) -> Optional[str]:
        return self._get_robot().get(ROBOT_KEYS.WIFI)

    def getUser(self) -> Optional[str]:
        return self._get_robot().get(ROBOT_KEYS.USER)
    
    def getPassword(self):
        return self._get_robot().get(ROBOT_KEYS.PASSWORD) # TODO: outsource into a .env file (e.g. .env/robot-credentials.env)
