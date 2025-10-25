from db.media.exceptions.MinioHelperError import MinioHelperError
from db.media.connector.MinioConnector import MinioConnector


class MinioHelper(MinioConnector):
    def __init__(self):
        super().__init__()

    def __enter__(self) -> "MinioHelper":
        self._connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client = None

    def list_buckets(self) -> list:
        try:
            buckets = self.client.list_buckets()
            return [bucket.name for bucket in buckets]
        except Exception as e:
            raise MinioHelperError(exception=e, error_code=1761341430)

    def list_objects(self, bucket_name: str, recursive: bool = True) -> list:
        try:
            objects = self.client.list_objects(bucket_name, recursive=recursive)
            return [obj.object_name for obj in objects]
        except Exception as e:
            raise MinioHelperError(exception=e, error_code=1761341440)

    def list_all(self, recursive: bool = True) -> dict:
        result = {}
        buckets = self.list_buckets()
        for bucket in buckets:
            result[bucket] = self.list_objects(bucket, recursive=recursive)
        return result
