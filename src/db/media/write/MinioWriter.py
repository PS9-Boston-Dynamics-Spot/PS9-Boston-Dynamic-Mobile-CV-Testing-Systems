from db.media.connector.MinioConnector import MinioConnector
from db.media.exceptions.MinioWriterError import MinioWriterError

class MinioWriter(MinioConnector):
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        super().__init__()

    def __enter__(self) -> 'MinioWriter':
        self._connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client = None

    def __check_parameter(self, object_name: str, file_path: str, content_type: str):
        if not object_name:
            raise MinioWriterError(exception=ValueError("Object name is empty"), error_code=1761328790)
        if not file_path:
            raise MinioWriterError(exception=ValueError("File path is empty"), error_code=1761328800)
        if not content_type:
            raise MinioWriterError(exception=ValueError("Content type is empty"), error_code=1761328810)

    def __check_object_already_exists(self, object_name: str):
        try:
            return self.client.stat_object(bucket_name=self.bucket_name, object_name=object_name)
        except Exception as e:
            raise MinioWriterError(exception=e, error_code=1761328840)

    def put_media(self, object_name: str, file_path: str, content_type: str = "application/octet-stream") -> None:

        self.__check_parameter(object_name, file_path, content_type)

        if self.__check_object_already_exists(object_name):
            raise MinioWriterError(
                exception=ValueError(f"Object '{object_name}' already exists in bucket '{self.bucket_name}'"),
                error_code=1761328830
            )
        
        try:
            self.client.fput_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                file_path=file_path,
                content_type=content_type
            )
        except Exception as e:
            raise MinioWriterError(exception=e, error_code=1761328820)
        