from configs.loader.ConfigLoader import ConfigLoader
from typing import Dict, Any, Optional
from configs.enum.ConfigEnum import ConfigEnum, SQLITE_KEYS


class SqliteConfigReader(ConfigLoader):
    def __init__(self):
        super().__init__()
        self.__config = self.load_config(ConfigEnum.SQLITE_CONFIG)

    def _getSqlite(self) -> Dict[str, Any]:
        value = self.__config.get(SQLITE_KEYS.SQLITE)
        if not isinstance(value, dict):
            return {}
        return value

    def getDatabase(self) -> Optional[str]:
        return self._getSqlite().get(SQLITE_KEYS.DATABASE)

    def getTimeout(self) -> Optional[int]:
        return self._getSqlite().get(SQLITE_KEYS.TIMEOUT)

    def getDetectTypes(self) -> Optional[int]:
        return self._getSqlite().get(SQLITE_KEYS.DETECT_TYPES)

    def getIsolationLevel(self) -> Optional[str]:
        return self._getSqlite().get(SQLITE_KEYS.ISOLATION_LEVEL)

    def getCheckSameThread(self) -> Optional[bool]:
        return self._getSqlite().get(SQLITE_KEYS.CHECK_SAME_THREAD)

    def getCachedStatements(self) -> Optional[int]:
        return self._getSqlite().get(SQLITE_KEYS.CACHED_STATEMENTS)

    def getUri(self) -> Optional[bool]:
        return self._getSqlite().get(SQLITE_KEYS.URI)
