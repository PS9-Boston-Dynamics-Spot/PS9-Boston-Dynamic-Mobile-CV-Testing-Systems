from common.exceptions.handler.LogHandler import LogHandler

class MinioConnectionError(BaseException):
    def __init__(self, exception: Exception, error_code: int):
        self.message = (
            f"Error: '{error_code}', Minio connection could not established, Exception: '{exception}'"
        )
        LogHandler.log_exception(self.message)

        super().__init__(self.message)
