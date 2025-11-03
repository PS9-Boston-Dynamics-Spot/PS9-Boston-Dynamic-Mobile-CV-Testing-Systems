from common.exceptions.BaseAppException import BaseAppException


class MediaRepositoryError(BaseAppException):
    def __init__(self, exception: Exception, error_code: int):
        self.message = f"Error: '{error_code}', MediaRepository could not access media, Exception: '{exception}'"
        super().__init__(self.message)
