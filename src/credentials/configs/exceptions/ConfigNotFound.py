from common.exceptions.BaseAppException import BaseAppException


class ConfigNotFound(BaseAppException):

    def __init__(self, exception: Exception, path: str, error_code: int):
        self.exception = exception
        self.path = path
        self.error_code = error_code
        self.message = f"Error: '{error_code}', Config not found for path '{path}', Exception: '{exception}'"
        super().__init__(self.message)
