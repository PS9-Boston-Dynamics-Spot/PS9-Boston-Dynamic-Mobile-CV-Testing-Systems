from db.meta.repository.MetaRepository import MetaRepository
from db.media.repository.MediaRepository import MediaRepository

from db.media.exceptions.MediaRepositoryError import MediaRepositoryError
from db.meta.exceptions.MetaRepositoryError import MetaRepositoryError
from db.dal.exceptions.DataAccessLayerError import DataAccessLayerError

from db.mapping.RawImageMapper import RawImageDTO


class DataAccessLayer:
    def __init__(self):
        pass

    def __enter__(self):
        self.meta_repository = MetaRepository()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def insert_raw_image(self, image_with_metadata: RawImageDTO) -> None:
        try:
            self.media_repository = MediaRepository(
                bucket_name=image_with_metadata.bucket
            )

            new_id = self.meta_repository.get_new_id()
            print("New ID: ", new_id)
            object_name = (
                f"{new_id}_{image_with_metadata.name}.{image_with_metadata.format}"
            )

            id, name = self.meta_repository.insert_raw_image(
                metadata=image_with_metadata
            )
            print("ID: ", id)
            print("Name: ", name)
            self.media_repository.put_media(
                object_name=object_name,
                image_data=image_with_metadata.image_data,
                content_type=image_with_metadata.content_type,
            )
        except MetaRepositoryError as e:
            raise DataAccessLayerError(exception=e, error_code=1761502460)
        except MediaRepositoryError as e:
            raise DataAccessLayerError(exception=e, error_code=1761502470)
        except Exception as e:
            raise DataAccessLayerError(exception=e, error_code=1761502480)

    def insert_analyzed_image(self):
        pass
