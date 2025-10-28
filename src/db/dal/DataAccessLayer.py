from db.meta.repository.MetaRepository import MetaRepository
from db.media.repository.MediaRepository import MediaRepository

from db.media.exceptions.MediaRepositoryError import MediaRepositoryError
from db.meta.exceptions.MetaRepositoryError import MetaRepositoryError
from db.dal.exceptions.DataAccessLayerError import DataAccessLayerError


class DataAccessLayer:
    def __init__(self):
        pass

    def __enter__(self):
        self.meta_repository = MetaRepository()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    # TODO: exception handling
    def __extract_metadata_raw_image(self, metadata: dict) -> tuple:
        image_data = metadata["image_data"]
        name = metadata["name"]
        format = metadata["format"]
        bucket = metadata["bucket"]
        size = metadata["size"]
        compressed = metadata["compressed"]
        compression_method = metadata["compression_method"]
        return image_data, name, format, bucket, size, compressed, compression_method

    def insert_raw_image(self, metadata: dict) -> None:
        try:
            image_data, name, format, bucket, size, compressed, compression_method = (
                self.__extract_metadata_raw_image(metadata)
            )
            self.media_repository = MediaRepository(bucket_name=bucket)

            content_type = self.media_repository.guess_content_type(
                image_data=image_data
            )

            new_id = self.meta_repository.get_new_id()
            print("New ID: ", new_id)
            object_name = f"{new_id}_{name}.{format}"

            id, name = self.meta_repository.insert_raw_image(
                name=object_name,
                format=format,
                content_type=content_type,
                bucket=bucket,
                size=size,
                compressed=compressed,
                compression_method=compression_method,
            )
            print("ID: ", id)
            print("Name: ", name)
            self.media_repository.put_media(
                object_name=object_name,
                image_data=image_data,
                content_type=content_type,
            )
        except MetaRepositoryError as e:
            raise DataAccessLayerError(exception=e, error_code=1761502460)
        except MediaRepositoryError as e:
            raise DataAccessLayerError(exception=e, error_code=1761502470)
        except Exception as e:
            raise DataAccessLayerError(exception=e, error_code=1761502480)

    def insert_analyzed_image(self):
        pass
