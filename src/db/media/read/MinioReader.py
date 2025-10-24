from db.media.connector.MinioConnector import MinioConnector
from db.media.exceptions.MinioReaderError import MinioReaderError
from minio.error import S3Error

class MinioReader(MinioConnector):
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        super().__init__()

    def __enter__(self) -> 'MinioReader':
        self._connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client = None

    def get_media(self, object_name: str) -> bytes:

        if not object_name:
            raise MinioReaderError(ValueError("Object name is missing"), 1761328580)

        try:
            response = self.client.get_object(self.bucket_name, object_name)
            data = response.read()
            return data
        except S3Error as e:
            # Speziell NoSuchKey behandeln
            if e.code == "NoSuchKey":
                raise MinioReaderError(
                    exception=ValueError(f"Object '{object_name}' does not exist in bucket '{self.bucket_name}'"),
                    error_code=1761339540
                )
        except Exception as e:
            raise MinioReaderError(exception=e, error_code=176132754)
        finally:
            if response:
                response.close()
                response.release_conn()
