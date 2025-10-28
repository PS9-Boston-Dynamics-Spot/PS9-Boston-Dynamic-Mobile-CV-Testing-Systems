from db.meta.connector.SqliteConnector import SqliteConnector
from db.meta.exceptions.SqliteConnectionError import SqliteConnectionError
from db.meta.exceptions.DatabaseWriterError import DatabaseWriterError
from sqlite3 import IntegrityError, OperationalError, DatabaseError


class DatabaseWriter(SqliteConnector):
    def __init__(self):
        self.connector = SqliteConnector()

    def insert_raw_image(
        self,
        name: str,
        format: str,
        content_type: str,
        bucket: str,
        size: int,
        compressed: bool,
        compression_method: str,
    ) -> tuple:
        query = """
            INSERT INTO cvision_images_raw (name, format, content_type, bucket, size, compressed, compression_method)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        try:
            with self.connector as cursor:
                cursor.execute(
                    query, (name, format, content_type, bucket, size, compressed, compression_method)
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

    def insert_analyzed_image(self) -> int:
        pass
