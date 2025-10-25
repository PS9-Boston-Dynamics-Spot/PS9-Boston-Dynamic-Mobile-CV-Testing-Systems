from sqlite3 import (
    connect,
    _IsolationLevel,
    OperationalError,
    DatabaseError,
    ProgrammingError,
    Row
)
from configs.reader.SqliteConfigReader import SqliteConfigReader
from db.meta.exceptions.SqliteConnectionError import SqliteConnectionError

VALID_ISOLATION_LEVELS: set[_IsolationLevel] = {
    "DEFERRED",
    "IMMEDIATE",
    "EXCLUSIVE",
    None,
}


class SqliteConnector:
    def __init__(self):
        self.sqlite_config_reader = SqliteConfigReader()
        self.database = self.sqlite_config_reader.getDatabase()
        self.timeout = self.sqlite_config_reader.getTimeout()
        self.detect_types = self.sqlite_config_reader.getDetectTypes()
        self.isolation_level = self.sqlite_config_reader.getIsolationLevel()
        self.check_same_thread = self.sqlite_config_reader.getCheckSameThread()
        self.cached_statements = self.sqlite_config_reader.getCachedStatements()
        self.uri = self.sqlite_config_reader.getUri()

        if self.isolation_level not in VALID_ISOLATION_LEVELS:
            raise SqliteConnectionError(
                exception=ValueError(
                    f"Invalid Isolation Level: {self.isolation_level}"
                ),
                error_code=1761423280,
            )

    def __enter__(self):
        try:
            self.connection = connect(
                database=self.database,
                timeout=self.timeout,
                detect_types=self.detect_types,
                isolation_level=self.isolation_level,
                check_same_thread=self.check_same_thread,
                cached_statements=self.cached_statements,
                uri=self.uri,
            )
            self.connection.row_factory = Row
            self.cursor = self.connection.cursor()
            return self.cursor
        except OperationalError as e:
            raise SqliteConnectionError(
                exception=RuntimeError(
                    f"SQLite operational error while connecting to '{self.database}': {e}"
                ),
                error_code=1761423240,
            )
        except ProgrammingError as e:
            raise SqliteConnectionError(
                exception=RuntimeError(f"SQLite programming error: {e}"),
                error_code=1761423250,
            )
        except DatabaseError as e:
            raise SqliteConnectionError(
                exception=RuntimeError(f"SQLite database error: {e}"),
                error_code=1761423260,
            )
        except Exception as e:
            raise SqliteConnectionError(
                exception=RuntimeError(f"Unexpected SQLite connection error: {e}"),
                error_code=1761423270,
            )

    def __exit__(self, exc_type, exc_value, traceback):
        if hasattr(self, "connection"):
            try:
                if exc_type is None:
                    self.connection.commit()
                else:
                    self.connection.rollback()
            finally:
                self.cursor.close()
                self.connection.close()
