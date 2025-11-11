from common.exceptions.BaseAppException import BaseAppException


class OPCUAConnectionRefusedError(BaseAppException):
    def __init__(self, exception: Exception, url: str, error_code: int):
        self.message = f"Error: '{error_code}', Connection refused to {url}, Exception: '{exception}'"
        super().__init__(self.message)
