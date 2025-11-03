from common.exceptions.BaseAppException import BaseAppException


class SqliteConnectionError(BaseAppException):
    def __init__(self, exception: Exception, error_code: int):
        self.message = f"Error: '{error_code}', Sqlite3 connection could not established, Exception: '{exception}'"
        super().__init__(self.message)
