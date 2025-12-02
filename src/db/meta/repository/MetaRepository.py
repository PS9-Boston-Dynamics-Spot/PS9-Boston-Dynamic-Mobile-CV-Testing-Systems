from db.meta.write.DatabaseWriter import DatabaseWriter
from db.meta.exceptions.DatabaseWriterError import DatabaseWriterError

from db.meta.exceptions.MetaRepositoryError import MetaRepositoryError

from db.mapping.RawImageMapper import RawImageDTO
from db.mapping.AnalyzedImageMapper import AnalyzedImageDTO
from db.mapping.AnomalyMapper import AnomalyDTO


class MetaRepository:
    def __init__(self):
        self.writer = DatabaseWriter()

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
                opcua_node_id=metadata.opcua_node_id,
                aruco_id=metadata.aruco_id,
                category=metadata.category,
                quality=metadata.quality,
                value=metadata.value,
                unit=metadata.unit,
            )
        except DatabaseWriterError as e:
            raise MetaRepositoryError(exception=e, error_code=1761932480)
        except Exception as e:
            raise MetaRepositoryError(exception=e, error_code=1761932490)

    def insert_anomaly(self, metadata: AnomalyDTO) -> int:
        try:
            return self.writer.insert_anomaly(
                analyzed_image_id=metadata.analyzed_image_id,
                detected_value=metadata.detected_value,
                is_anomaly=metadata.is_anomaly,
                anomaly_score=metadata.anomaly_score,
                node_id=metadata.node_id,
                parameters=metadata.parameters,
            )
        except DatabaseWriterError as e:
            raise MetaRepositoryError(exception=e, error_code=1762881900)
        except Exception as e:
            raise MetaRepositoryError(exception=e, error_code=1762881910)
