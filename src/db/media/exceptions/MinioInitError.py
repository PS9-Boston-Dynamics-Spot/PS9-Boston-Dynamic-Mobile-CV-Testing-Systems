from common.exceptions.BaseAppException import BaseAppException


class MinioInitError(BaseAppException):
    def __init__(self, exception: Exception, error_code: int, **args):
        self.exception = exception
        self.error_code = error_code
        self.extra = args
        self.message = f"Error: '{error_code}', MinIO configuration: {args}, Exception: '{exception}'"
        super().__init__(self.message)
