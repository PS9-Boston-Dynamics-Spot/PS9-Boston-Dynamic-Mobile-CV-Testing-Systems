from common.exceptions.BaseAppException import BaseAppException


class ConfigParseError(BaseAppException):

    def __init__(self, exception: Exception, error_code: int):
        self.exception = exception
        self.error_code = error_code
        self.message = (
            f"Error: '{error_code}', Config could not parsed, Exception: '{exception}'"
        )
        super().__init__(self.message)
