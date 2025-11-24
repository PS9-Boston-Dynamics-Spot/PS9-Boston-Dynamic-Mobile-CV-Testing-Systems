from configs.unified_config_manager import UnifiedConfigManager
import sqlite3

class SqliteConnector:
    def __init__(self, config_manager: UnifiedConfigManager | None = None) -> None:
        self._config_manager = config_manager or UnifiedConfigManager()
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        cfg = self._config_manager.getDBCreds()
        self._conn = sqlite3.connect(
            cfg["database"],
            timeout=cfg["timeout"],
            detect_types=cfg["detect_types"],
            isolation_level=cfg["isolation_level"],
            check_same_thread=cfg["check_same_thread"],
            cached_statements=cfg["cached_statements"],
            uri=cfg["uri"],
        )
        return self._conn
