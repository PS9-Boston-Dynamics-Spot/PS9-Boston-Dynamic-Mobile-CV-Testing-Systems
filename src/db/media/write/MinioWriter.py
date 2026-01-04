import io
from db.media.connector.MinioConnector import MinioConnector
from db.media.exceptions.MinioWriterError import MinioWriterError
from minio.error import S3Error


class MinioWriter(MinioConnector):
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        super().__init__()

    def __enter__(self) -> "MinioWriter":
        self._connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client = None

    def __get_bytes_length(self, image_data: bytes) -> int:
        return len(image_data)

    def __check_object_already_exists(self, object_name: str) -> bool:
        try:
            self.client.stat_object(
                bucket_name=self.bucket_name, object_name=object_name
            )
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            else:
                raise MinioWriterError(exception=e, error_code=1761328840)

    def put_media(
        self,
        object_name: str,
        image_data: bytes,
        content_type: str,
    ) -> None:

        if self.__check_object_already_exists(object_name):
            raise MinioWriterError(
                exception=ValueError(
                    f"Object '{object_name}' already exists in bucket '{self.bucket_name}'"
                ),
                error_code=1761328830,
            )

        try:
            data_stream = io.BytesIO(image_data)
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=data_stream,
                length=self.__get_bytes_length(image_data=image_data),
                content_type=content_type,
            )
        except Exception as e:
            raise MinioWriterError(exception=e, error_code=1761328820)
