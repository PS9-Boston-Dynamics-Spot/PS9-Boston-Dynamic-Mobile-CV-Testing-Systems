from db.meta.read.DatabaseReader import DatabaseReader
from db.meta.write.DatabaseWriter import DatabaseWriter
from db.meta.exceptions.DatabaseWriterError import DatabaseWriterError

from db.meta.exceptions.MetaRepositoryError import MetaRepositoryError

class MetaRepository:
    def __init__(self):
        self.reader = DatabaseReader()
        self.writer = DatabaseWriter()

    def insert_raw_image(self, name: str, format: str, bucket: str, size: int, compressed: bool, compression_method: str) -> int:
        try:
            return self.writer.insert_raw_image(name, format, bucket, size, compressed, compression_method)
        except DatabaseWriterError as e:
            raise MetaRepositoryError(exception=e, error_code=1761492730)
        except Exception as e:
            raise MetaRepositoryError(exception=e, error_code=1761492740)
        
    def get_new_id(self):
        return self.reader.get_new_id()

    def insert_analyzed_image(self):
        pass