from common.exceptions.BaseAppException import BaseAppException


class CenterNotFound(BaseAppException):
    def __init__(self, error_code: int):
        self.error_code = error_code
        self.message = (
            f"Error: '{error_code}', Center could not be found in the sensor image"
        )
        super().__init__(self.message)
