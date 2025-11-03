from common.exceptions.BaseAppException import BaseAppException


class BucketInitializerError(BaseAppException):
    def __init__(self, exception: Exception, error_code: int):
        self.message = f"Error: '{error_code}', BucketInitializer could not create init Bucket, Exception: '{exception}'"
        super().__init__(self.message)
