from common.exceptions.BaseAppException import BaseAppException

class MetaRepositoryError(BaseAppException):
    def __init__(self, exception: Exception, error_code: int):
        self.message = f"Error: '{error_code}', MetaRepository could not write / read metadata for the image, Exception: '{exception}'"
        super().__init__(self.message)
