from db.media.read.MinioReader import MinioReader
from db.media.write.MinioWriter import MinioWriter
from db.media.infrastructure.BucketCreator import BucketCreator
from db.media.infrastructure.MinioBucketInitializer import MinioBucketInitializer

from db.media.exceptions.MinioWriterError import MinioWriterError
from db.media.exceptions.MinioReaderError import MinioReaderError
from db.media.exceptions.BucketCreatorError import BucketCreatorError
from db.media.exceptions.BucketInitializerError import BucketInitializerError
from db.media.exceptions.MediaRepositoryError import MediaRepositoryError

class MediaRepository:
    def __init__(self, bucket_name: str):
        """
        Initializes the MediaRepository object with the given bucket name.

        Parameters:
        bucket_name (str): The name of the bucket to be used.

        Returns:
        None
        """
        self.bucket_name = bucket_name

    def __initialize_bucket(self) -> str:
        """
        Initializes the bucket by checking if it exists and creating it if not.
        
        Raises:
        MediaRepositoryError: If the bucket cannot be initialized.
        """
        print("BUCKET NAME", self.bucket_name)
        if self.bucket_name is None:
            raise ValueError("Bucket name is None")

        try:
            return MinioBucketInitializer(self.bucket_name).initalize_bucket()
        except BucketInitializerError as e:
            # TODO: Improve error handling, e.g. try again? 
            raise MediaRepositoryError(exception=e, error_code=1761337500)
        except Exception as e:
            raise MediaRepositoryError(exception=e, error_code=1761337600)

    def get_media(self, object_name: str) -> bytes:
        """
        Downloads a file from the specified bucket with the given name.
        
        Parameters:
        object_name (str): The name of the object to be downloaded.
        
        Returns:
        bytes: The content of the object.
        
        Raises:
        MediaRepositoryError: If there is an issue with the bucket or the object.
        """
        try:
            bucket_name = self.__initialize_bucket()
            with MinioReader(bucket_name) as minio:
                return minio.get_media(object_name)
        except MinioReaderError as e:
            # TODO: Improve error handling, e.g. try again? 
            raise MediaRepositoryError(exception=e, error_code=1761332260)
        except Exception as e:
            raise MediaRepositoryError(exception=e, error_code=1761332270)

    def put_media(self, object_name: str, file_path: str, content_type: str = "application/octet-stream") -> None:
        """
        Uploads a file to the specified bucket with the given name and content type.
        
        Parameters:
        object_name (str): The name of the object to be uploaded.
        file_path (str): The path to the file to be uploaded.
        content_type (str): The content type of the file to be uploaded.

        Raises:
        MediaRepositoryError: If there is an issue with the bucket or the object.
        """
        try:
            bucket_name = self.__initialize_bucket()
            with MinioWriter(bucket_name) as minio:
                minio.put_media(object_name, file_path, content_type)
        except MinioWriterError as e:
            # TODO: Improve error handling, e.g. try again? 
            raise MediaRepositoryError(exception=e, error_code=1761332280)
        except Exception as e:
            raise MediaRepositoryError(exception=e, error_code=1761332290)
        
        # TODO: list buckets / objects / all