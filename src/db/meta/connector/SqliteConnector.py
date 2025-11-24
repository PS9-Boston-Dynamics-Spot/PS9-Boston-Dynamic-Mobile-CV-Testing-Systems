from sqlite3 import connect
from credentials.configs.reader.SqliteConfigReader import SqliteConfigReader
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
    _shared_connection = None  # zentrale, geteilte Verbindung
    _lock = threading.Lock()  # Thread-Sicherheit

    def __init__(self):
        if SqliteConnector._shared_connection is None:
            self._init_shared_connection()
        self.connection = SqliteConnector._shared_connection

    def _init_shared_connection(self):
        with SqliteConnector._lock:
            if SqliteConnector._shared_connection is not None:
                return  # wurde schon initialisiert

            config = SqliteConfigReader()
            isolation_level = config.getIsolationLevel()

            if isolation_level not in VALID_ISOLATION_LEVELS:
                raise SqliteConnectionError(
                    exception=ValueError(f"Invalid Isolation Level: {isolation_level}"),
                    error_code=1761423280,
                )

            SqliteConnector._shared_connection = connect(
                database=config.getDatabase(),
                timeout=config.getTimeout(),
                detect_types=config.getDetectTypes(),
                isolation_level=isolation_level,
                check_same_thread=config.getCheckSameThread(),
                cached_statements=config.getCachedStatements(),
                uri=config.getUri(),
            )

            print("SQLite shared connection established.")

    def _ensure_connection(self):
        if SqliteConnector._shared_connection is None:
            print("Reconnecting to SQLite database...")
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
                print("SQLite shared connection closed.")
                cls._shared_connection.close()
                cls._shared_connection = None
