from db.media.connector.MinioConnector import MinioConnector
from db.media.exceptions.MinioReaderError import MinioReaderError


class MinioReader(MinioConnector):
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        super().__init__()

    def __enter__(self) -> "MinioReader":
        self._connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client = None

    def get_media(self, object_name: str) -> bytes:
        try:
            return self.client.get_object(
                bucket_name=self.bucket_name, object_name=object_name
            )
        except Exception as e:
            raise MinioReaderError(
                exception=e,
                error_code=1763313860,
                bucket_name=self.bucket_name,
                object_name=object_name,
            )
