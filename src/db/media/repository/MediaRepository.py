from db.media.write.MinioWriter import MinioWriter
from db.media.infrastructure.MinioBucketInitializer import MinioBucketInitializer

from db.media.exceptions.MinioWriterError import MinioWriterError
from db.media.exceptions.BucketInitializerError import BucketInitializerError
from db.media.exceptions.MediaRepositoryError import MediaRepositoryError


class MediaRepository:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name

    def __initialize_bucket(self) -> str:
        try:
            return MinioBucketInitializer(self.bucket_name).initalize_bucket()
        except BucketInitializerError as e:
            # TODO: Improve error handling, e.g. try again?
            raise MediaRepositoryError(exception=e, error_code=1761337500)
        except Exception as e:
            raise MediaRepositoryError(exception=e, error_code=1761337600)

    def put_media(self, object_name: str, image_data: bytes, content_type: str) -> None:
        try:
            bucket_name = self.__initialize_bucket()
            with MinioWriter(bucket_name) as minio:
                print("Conten Type:", content_type)
                minio.put_media(
                    object_name=object_name,
                    image_data=image_data,
                    content_type=content_type,
                )
        except MinioWriterError as e:
            # TODO: Improve error handling, e.g. try again?
            raise MediaRepositoryError(exception=e, error_code=1761332280)
        except Exception as e:
            raise MediaRepositoryError(exception=e, error_code=1761332290)