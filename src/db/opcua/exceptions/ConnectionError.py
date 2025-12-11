from common.exceptions.BaseAppException import BaseAppException


class ConnectionError(BaseAppException):
    def __init__(self, exception: Exception, url: str, error_code: int):
        self.exeption = exception
        self.url = url
        self.error_code = error_code
        self.message = f"Error: '{error_code}', Unknown OpcUa connection error to {url}, Exception: '{exception}'"
        super().__init__(self.message)
