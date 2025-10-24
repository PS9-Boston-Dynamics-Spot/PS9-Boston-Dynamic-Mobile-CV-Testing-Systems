from common.exceptions.BaseAppException import BaseAppException

class MinioHelperError(BaseAppException):
    def __init__(self, exception: Exception, error_code: int):
        self.message = (f"Error: '{error_code}', MinioHelper could not list buckets / objects, Exception: '{exception}'")
        super().__init__(self.message)
