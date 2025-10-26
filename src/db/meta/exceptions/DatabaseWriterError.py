from common.exceptions.BaseAppException import BaseAppException

class DatabaseWriterError(BaseAppException):
    def __init__(self, exception: Exception, error_code: int):
        self.message = f"Error: '{error_code}', Database could not write metadata for the image, Exception: '{exception}'"
        super().__init__(self.message)