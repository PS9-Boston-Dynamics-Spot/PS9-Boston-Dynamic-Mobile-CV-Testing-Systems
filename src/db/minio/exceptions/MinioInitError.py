from common.exceptions.handler.LogHandler import LogHandler

class MinioInitError(BaseException):
    def __init__(self, exception: Exception, error_code: int, **args):
        self.message = (
            f"Error: '{error_code}', MinIO configuration: {args}, Exception: '{exception}'"
        )
        LogHandler.log_exception(self.message)

        super().__init__(self.message)