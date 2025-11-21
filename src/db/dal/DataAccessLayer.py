from typing import Any

from db.meta.repository.MetaRepository import MetaRepository
from db.media.repository.MediaRepository import MediaRepository
from db.opcua.repository.OPCUARepository import OPCUARepository

from db.media.exceptions.MediaRepositoryError import MediaRepositoryError
from db.meta.exceptions.MetaRepositoryError import MetaRepositoryError
from db.dal.exceptions.DataAccessLayerError import DataAccessLayerError
from db.opcua.exceptions.OPCUARepositoryError import OPCUARepositoryError

from db.mapping.RawImageMapper import RawImageDTO
from db.mapping.AnalyzedImageMapper import AnalyzedImageDTO
from db.mapping.AnomalyMapper import AnomalyDTO


class DataAccessLayer:
    def __init__(self):
        pass

    def __enter__(self):
        self.meta_repository = MetaRepository()
        self.opcua_repository = OPCUARepository()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def create_object_name(self, id: int, name: str, format: str) -> str:
        safe_name = name.replace(" ", "_").lower()
        return f"{id}_{safe_name}.{format}"

    def insert_raw_image(self, raw_image_with_metadata: RawImageDTO) -> int:
        try:
            self.media_repository = MediaRepository(
                bucket_name=raw_image_with_metadata.bucket
            )

            new_id = self.meta_repository.get_new_id_raw_images()
            object_name = self.create_object_name(
                id=new_id,
                name=raw_image_with_metadata.name,
                format=raw_image_with_metadata.format,
            )

            id, name = self.meta_repository.insert_raw_image_metadata(
                metadata=raw_image_with_metadata
            )

            self.media_repository.put_media(
                object_name=object_name,
                image_data=raw_image_with_metadata.image_data,
                content_type=raw_image_with_metadata.content_type,
            )
            return id
        except MetaRepositoryError as e:
            raise DataAccessLayerError(exception=e, error_code=1761502460)
        except MediaRepositoryError as e:
            raise DataAccessLayerError(exception=e, error_code=1761502470)
        except Exception as e:
            raise DataAccessLayerError(exception=e, error_code=1761502480)

    def insert_analyzed_image(
        self, anaylzed_image_with_metadata: AnalyzedImageDTO
    ) -> id:
        try:
            self.media_repository = MediaRepository(
                bucket_name=anaylzed_image_with_metadata.bucket
            )

            new_id = self.meta_repository.get_new_id_analyzed_images()
            object_name = self.create_object_name(
                id=new_id,
                name=anaylzed_image_with_metadata.name,
                format=anaylzed_image_with_metadata.format,
            )

            id, name = self.meta_repository.insert_analyzed_image_metadata(
                metadata=anaylzed_image_with_metadata
            )

            self.media_repository.put_media(
                object_name=object_name,
                image_data=anaylzed_image_with_metadata.image_data,
                content_type=anaylzed_image_with_metadata.content_type,
            )

            return id

        except MetaRepositoryError as e:
            raise DataAccessLayerError(exception=e, error_code=1761932730)
        except MediaRepositoryError as e:
            raise DataAccessLayerError(exception=e, error_code=1761932740)
        except Exception as e:
            raise DataAccessLayerError(exception=e, error_code=1761932750)

    def insert_anomaly(self, anomaly_with_metadata: AnomalyDTO) -> None:
        try:
            self.meta_repository.insert_anomaly(metadata=anomaly_with_metadata)
        except MetaRepositoryError as e:
            raise DataAccessLayerError(exception=e, error_code=1762882020)
        except Exception as e:
            raise DataAccessLayerError(exception=e, error_code=1762882030)

    def get_value_from_opcua_node(self, opcua_node_id: str) -> Any:
        try:
            return self.opcua_repository.get_node_value_by_id(
                opcua_node_id=opcua_node_id
            )
        except OPCUARepositoryError as e:
            raise DataAccessLayerError(exception=e, error_code=1762858740)
        except Exception as e:
            raise DataAccessLayerError(exception=e, error_code=1762858750)
