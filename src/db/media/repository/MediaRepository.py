from db.media.read.MinioReader import MinioReader
from db.media.write.MinioWriter import MinioWriter
from db.media.infrastructure.MinioBucketInitializer import MinioBucketInitializer
from db.media.read.MinioHelper import MinioHelper
import imghdr

from db.media.exceptions.MinioWriterError import MinioWriterError
from db.media.exceptions.MinioReaderError import MinioReaderError
from db.media.exceptions.BucketInitializerError import BucketInitializerError
from db.media.exceptions.MediaRepositoryError import MediaRepositoryError
from db.media.exceptions.MinioHelperError import MinioHelperError

import mimetypes


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

    def get_media(self, object_name: str) -> bytes:
        try:
            bucket_name = self.__initialize_bucket()
            with MinioReader(bucket_name) as minio:
                return minio.get_media(object_name)
        except MinioReaderError as e:
            # TODO: Improve error handling, e.g. try again?
            raise MediaRepositoryError(exception=e, error_code=1761332260)
        except Exception as e:
            raise MediaRepositoryError(exception=e, error_code=1761332270)

    def guess_content_type(self, image_data: bytes) -> str:
        if image_data:
            detected = imghdr.what(None, h=image_data)
            if detected == "jpeg":
                return "image/jpeg"
            elif detected == "png":
                return "image/png"
            elif detected == "bmp":
                return "image/bmp"
            elif detected == "tiff":
                return "image/tiff"
            else:
                return "application/octet-stream"

        return "application/octet-stream"

    def put_media(
        self,
        object_name: str,
        image_data: bytes,
        content_type: str
    ) -> None:
        try:
            bucket_name = self.__initialize_bucket()
            with MinioWriter(bucket_name) as minio:
                print("Conten Type:", content_type)
                minio.put_media(object_name=object_name, image_data=image_data, content_type=content_type)
        except MinioWriterError as e:
            # TODO: Improve error handling, e.g. try again?
            raise MediaRepositoryError(exception=e, error_code=1761332280)
        except Exception as e:
            raise MediaRepositoryError(exception=e, error_code=1761332290)

        # TODO: list buckets / objects / all

    @staticmethod
    def get_buckets() -> list:
        try:
            with MinioHelper() as minio:
                return minio.list_buckets()
        except MinioHelperError as e:
            # TODO: Improve error handling, e.g. try again?
            raise MediaRepositoryError(exception=e, error_code=1761401990)
        except Exception as e:
            raise MediaRepositoryError(exception=e, error_code=1761402000)

    def get_objects(self) -> list:
        try:
            with MinioHelper() as minio:
                return minio.list_objects(self.bucket_name)
        except MinioHelperError as e:
            # TODO: Improve error handling, e.g. try again?
            raise MediaRepositoryError(exception=e, error_code=1761402010)
        except Exception as e:
            raise MediaRepositoryError(exception=e, error_code=1761402020)

    @staticmethod
    def get_everything_recursive(recursive: bool = True) -> dict:
        try:
            with MinioHelper() as minio:
                return minio.list_all(recursive=recursive)
        except MinioHelperError as e:
            # TODO: Improve error handling, e.g. try again?
            raise MediaRepositoryError(exception=e, error_code=1761402030)
        except Exception as e:
            raise MediaRepositoryError(exception=e, error_code=1761402040)
