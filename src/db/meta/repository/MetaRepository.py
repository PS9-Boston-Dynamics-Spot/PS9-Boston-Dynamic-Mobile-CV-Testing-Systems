from db.meta.read.DatabaseReader import DatabaseReader
from db.meta.write.DatabaseWriter import DatabaseWriter
from db.meta.exceptions.DatabaseWriterError import DatabaseWriterError

from db.meta.exceptions.MetaRepositoryError import MetaRepositoryError

from db.mapping.RawImageMapper import RawImageDTO
from db.mapping.AnalyzedImageMapper import AnalyzedImageDTO


class MetaRepository:
    def __init__(self):
        self.reader = DatabaseReader()
        self.writer = DatabaseWriter()

    def get_new_id_raw_images(self) -> int:
        return self.reader.get_new_id_raw_images()
    
    def get_new_id_analyzed_images(self) -> int:
        return self.reader.get_new_id_analyzed_images()

    def insert_raw_image_metadata(
        self,
        metadata: RawImageDTO,
    ) -> tuple[int, str]:
        try:
            return self.writer.insert_raw_image_metadata(
                name=metadata.name,
                format=metadata.format,
                content_type=metadata.content_type,
                bucket=metadata.bucket,
                size=metadata.size,
                compressed=metadata.compressed,
                compression_method=metadata.compression_method,
            )
        except DatabaseWriterError as e:
            raise MetaRepositoryError(exception=e, error_code=1761492730)
        except Exception as e:
            raise MetaRepositoryError(exception=e, error_code=1761492740)

    def insert_analyzed_image_metadata(
        self, metadata: AnalyzedImageDTO
    ) -> tuple[int, str]:
        try:
            return self.writer.insert_analyzed_image_metadata(
                name=metadata.name,
                raw_image_id=metadata.raw_image_id,
                format=metadata.format,
                content_type=metadata.content_type,
                bucket=metadata.bucket,
                size=metadata.size,
                compressed=metadata.compressed,
                compression_method=metadata.compression_method,
                sensor_type=metadata.sensor_type,
                category=metadata.category,
                quality=metadata.quality,
                value=metadata.value,
                unit=metadata.unit,
            )
        except DatabaseWriterError as e:
            raise MetaRepositoryError(exception=e, error_code=1761932480)
        except Exception as e:
            raise MetaRepositoryError(exception=e, error_code=1761932490)
