from sqlite3 import connect
from credentials.manager.UnifiedCredentialsManager import UnifiedCredentialsManager
from db.meta.exceptions.SqliteConnectionError import SqliteConnectionError
from typing import Optional, Literal
import threading

IsolationLevel = Optional[Literal["DEFERRED", "IMMEDIATE", "EXCLUSIVE"]]

VALID_ISOLATION_LEVELS: set[IsolationLevel] = {
    "DEFERRED",
    "IMMEDIATE",
    "EXCLUSIVE",
    None,
}


class SqliteConnector:
    _shared_connection = None
    _lock = threading.Lock()

    def __init__(self):
        if SqliteConnector._shared_connection is None:
            self._init_shared_connection()
        self.connection = SqliteConnector._shared_connection

    def _init_shared_connection(self):
        with SqliteConnector._lock:
            if SqliteConnector._shared_connection is not None:
                return

            config_manager = UnifiedCredentialsManager()
            credentials = config_manager.getDBCredentials()
            isolation_level = credentials["isolation_level"]

            if isolation_level not in VALID_ISOLATION_LEVELS:
                raise SqliteConnectionError(
                    exception=ValueError(f"Invalid Isolation Level: {isolation_level}"),
                    error_code=1761423280,
                )

            SqliteConnector._shared_connection = connect(
                database=credentials["database"],
                timeout=credentials["timeout"],
                detect_types=credentials["detect_types"],
                isolation_level=isolation_level,
                check_same_thread=credentials["check_same_thread"],
                cached_statements=credentials["cached_statements"],
                uri=credentials["uri"],
            )

    def _ensure_connection(self):
        if SqliteConnector._shared_connection is None:
            self._init_shared_connection()
        self.connection = SqliteConnector._shared_connection

    def __enter__(self):
        self._ensure_connection()
        self._lock.acquire()
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is None:
                try:
                    self.connection.commit()
                except Exception as e:
                    print(f"[WARN] Commit failed: {e}")
            else:
                try:
                    self.connection.rollback()
                except Exception as e:
                    print(f"[WARN] Rollback failed: {e}")
        finally:
            if hasattr(self, "cursor") and self.cursor:
                try:
                    self.cursor.close()
                except Exception:
                    pass
            self._lock.release()

    @classmethod
    def close(cls):
        with cls._lock:
            if cls._shared_connection:
                cls._shared_connection.close()
                cls._shared_connection = None
