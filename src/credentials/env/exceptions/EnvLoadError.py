from common.exceptions.BaseAppException import BaseAppException


class EnvLoadError(BaseAppException):

    def __init__(self, exception: Exception, error_code: int):
        self.message = (
            f"Error: '{error_code}', Env could not loaded, Exception: '{exception}'"
        )
        super().__init__(self.message)