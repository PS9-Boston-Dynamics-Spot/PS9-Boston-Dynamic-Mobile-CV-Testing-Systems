from common.exceptions.BaseAppException import BaseAppException


class ConnectionRefusedError(BaseAppException):
    def __init__(self, exception: Exception, error_code: int):
        self.message = f"Error: '{error_code}', Connection refused, Exception: '{exception}'"
        super().__init__(self.message)
