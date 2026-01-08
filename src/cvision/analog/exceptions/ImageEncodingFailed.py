from common.exceptions.BaseAppException import BaseAppException


class ImageEncodingFailed(BaseAppException):
    def __init__(self, error_code: int):
        self.error_code = error_code
        self.message = f"Error: '{error_code}', Image could not be logged"
        super().__init__(self.message)
