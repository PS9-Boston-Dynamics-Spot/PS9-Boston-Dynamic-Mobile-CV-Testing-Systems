from db.meta.manager.SqliteConnectionManager import SqliteConnectionManager
from db.meta.exceptions.SqliteConnectionError import SqliteConnectionError
from db.meta.exceptions.DatabaseWriterError import DatabaseWriterError
from sqlite3 import IntegrityError, OperationalError, DatabaseError


class DatabaseWriter:
    def __init__(self):
        self.connector = SqliteConnectionManager.get_connector()

    def insert_raw_image_metadata(
        self,
        name: str,
        format: str,
        content_type: str,
        bucket: str,
        size: int,
        compressed: bool,
        compression_method: str,
    ) -> tuple[int, str]:
        query = """
            INSERT INTO cvision_images_raw (
                name, 
                format, 
                content_type, 
                bucket, 
                size, 
                compressed, 
                compression_method)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        try:
            with self.connector as cursor:
                cursor.execute(
                    query,
                    (
                        name,
                        format,
                        content_type,
                        bucket,
                        size,
                        compressed,
                        compression_method,
                    ),
                )
                return cursor.lastrowid, name
        except IntegrityError as e:
            raise DatabaseWriterError(exception=e, error_code=1761492340)
        except OperationalError as e:
            raise DatabaseWriterError(exception=e, error_code=1761492350)
        except DatabaseError as e:
            raise DatabaseWriterError(exception=e, error_code=1761492360)
        except SqliteConnectionError as e:
            raise DatabaseWriterError(exception=e, error_code=1761492370)
        except Exception as e:
            raise DatabaseWriterError(exception=e, error_code=1761492380)

    def insert_analyzed_image_metadata(
        self,
        name: str,
        raw_image_id: int,
        format: str,
        content_type: str,
        bucket: str,
        size: int,
        compressed: bool,
        compression_method: str,
        sensor_type: str,
        opcua_node_id: str,
        aruco_id: int,
        value: float,
        unit: str,
        category: str,
    ) -> tuple[int, str]:
        query = """
            INSERT INTO cvision_images_analyzed (
                raw_image_id,
                name, 
                format, 
                content_type, 
                bucket, 
                size, 
                compressed, 
                compression_method, 
                sensor_type,
                opcua_node_id,
                aruco_id,
                value, 
                unit,
                category
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        try:
            with self.connector as cursor:
                cursor.execute(
                    query,
                    (
                        raw_image_id,
                        name,
                        format,
                        content_type,
                        bucket,
                        size,
                        compressed,
                        compression_method,
                        sensor_type,
                        opcua_node_id,
                        aruco_id,
                        value,
                        unit,
                        category,
                    ),
                )
                return cursor.lastrowid, name
        except IntegrityError as e:
            raise DatabaseWriterError(exception=e, error_code=1761929140)
        except OperationalError as e:
            raise DatabaseWriterError(exception=e, error_code=1761929150)
        except DatabaseError as e:
            raise DatabaseWriterError(exception=e, error_code=1761929160)
        except SqliteConnectionError as e:
            raise DatabaseWriterError(exception=e, error_code=1761929170)
        except Exception as e:
            raise DatabaseWriterError(exception=e, error_code=1761929180)

    def insert_anomaly(
        self,
        analyzed_image_id: int,
        is_anomaly: bool,
        anomaly_score: float,
        used_funtion: str,
        parameters: str,
    ) -> int:
        query = """
            INSERT INTO anomalies (
                analyzed_image_id,
                is_anomaly,
                anomaly_score,
                used_function,
                parameters
            )
            VALUES (?, ?, ?, ?, ?);
        """

        try:
            with self.connector as cursor:
                cursor.execute(
                    query,
                    (
                        analyzed_image_id,
                        is_anomaly,
                        anomaly_score,
                        used_funtion,
                        parameters,
                    ),
                )
                return cursor.lastrowid
        except IntegrityError as e:
            raise DatabaseWriterError(exception=e, error_code=1762880810)
        except OperationalError as e:
            raise DatabaseWriterError(exception=e, error_code=1762880820)
        except DatabaseError as e:
            raise DatabaseWriterError(exception=e, error_code=1762880830)
        except SqliteConnectionError as e:
            raise DatabaseWriterError(exception=e, error_code=1762880840)
        except Exception as e:
            raise DatabaseWriterError(exception=e, error_code=1762880850)
