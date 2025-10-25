from db.media.connector.MinioConnector import MinioConnector
from db.media.exceptions.BucketCreatorError import BucketCreatorError


class BucketCreator(MinioConnector):

    def __init__(self):
        super().__init__()
        self._connect()

    def bucket_exists(self, bucket_name: str) -> bool:
        try:
            with self as client:
                return client.bucket_exists(bucket_name)
        except Exception as e:
            raise BucketCreatorError(exception=e, error_code=1761337400)

    def ensure_bucket(self, bucket_name: str) -> str:
        try:
            with self as client:
                if not client.bucket_exists(bucket_name):
                    client.make_bucket(bucket_name)
                return bucket_name
        except ValueError as e:
            raise BucketCreatorError(exception=e, error_code=1761335030)
        except Exception as e:
            raise BucketCreatorError(exception=e, error_code=1761335040)
