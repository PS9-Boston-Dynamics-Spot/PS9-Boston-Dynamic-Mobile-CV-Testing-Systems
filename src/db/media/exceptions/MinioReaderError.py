from common.exceptions.BaseAppException import BaseAppException

class MinioReaderError(BaseAppException):
    def __init__(self, exception: Exception, error_code: int):
        self.message = (f"Error: '{error_code}', Minio could not read media, Exception: '{exception}'")
        super().__init__(self.message)