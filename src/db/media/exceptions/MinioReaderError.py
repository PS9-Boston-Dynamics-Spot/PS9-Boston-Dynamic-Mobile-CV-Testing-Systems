from common.exceptions.BaseAppException import BaseAppException


class MinioReaderError(BaseAppException):
    def __init__(
        self, exception: Exception, error_code: int, bucket_name: str, object_name: str
    ):
        self.message = f"Error: '{error_code}', MinIO could not read media, Bucket: {bucket_name}, Object: {object_name}, Exception: '{exception}'"
        super().__init__(self.message)
