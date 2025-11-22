from common.exceptions.BaseAppException import BaseAppException


class OPCUARepositoryError(BaseAppException):
    def __init__(self, exception: Exception, error_code: int):
        self.exeption = exception
        self.error_code = error_code
        self.message = (
            f"Error: '{error_code}', OPCUA-Repository Error, Exception: '{exception}'"
        )
        super().__init__(self.message)
