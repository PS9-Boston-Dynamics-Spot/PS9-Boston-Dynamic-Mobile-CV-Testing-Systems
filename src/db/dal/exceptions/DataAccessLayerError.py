from common.exceptions.BaseAppException import BaseAppException


class DataAccessLayerError(BaseAppException):
    def __init__(self, exception: Exception, error_code: int):
        self.message = f"Error: '{error_code}', DataAccessLayer could not read / write, Exception: '{exception}'"
        super().__init__(self.message)
