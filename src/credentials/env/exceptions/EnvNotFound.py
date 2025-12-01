from common.exceptions.BaseAppException import BaseAppException


class EnvNotFound(BaseAppException):

    def __init__(self, exception: Exception, path: str, error_code: int):

        self.message = f"Error: '{error_code}', Env not found for path '{path}', Exception: '{exception}'"
        super().__init__(self.message)
