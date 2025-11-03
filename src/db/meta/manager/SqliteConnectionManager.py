import atexit
from db.meta.connector.SqliteConnector import SqliteConnector


class SqliteConnectionManager:
    _instance = None

    @classmethod
    def get_connector(cls) -> SqliteConnector:
        if cls._instance is None:
            cls._instance = SqliteConnector()
        return cls._instance

    @classmethod
    def close(cls):
        if cls._instance:
            cls._instance.close()
            cls._instance = None


atexit.register(SqliteConnectionManager.close)
