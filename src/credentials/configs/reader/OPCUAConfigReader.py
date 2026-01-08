from common.imports.Typing import Optional, Dict, Any
from credentials.configs.loader.ConfigLoader import ConfigLoader
from credentials.configs.enum.ConfigEnum import ConfigEnum, OPCUA_KEYS


class OPCUAConfigReader(ConfigLoader):
    def __init__(self):
        super().__init__()
        self.__config = self.load_config(ConfigEnum.OPCUA_CONFIG)

    def _getOPCUA(self) -> Dict[str, Any]:
        value = self.__config.get(OPCUA_KEYS.OPCUA)
        if not isinstance(value, dict):
            return {}
        return value

    def getIp(self) -> Optional[str]:
        return self._getOPCUA().get(OPCUA_KEYS.IP)

    def getPort(self) -> Optional[int]:
        return self._getOPCUA().get(OPCUA_KEYS.PORT)

    def getProtocol(self) -> Optional[str]:
        return self._getOPCUA().get(OPCUA_KEYS.PROTOCOL)

    def getTimeout(self) -> Optional[int]:
        return self._getOPCUA().get(OPCUA_KEYS.TIMEOUT)
