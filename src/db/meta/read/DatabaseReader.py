from db.meta.manager.SqliteConnectionManager import SqliteConnectionManager


class DatabaseReader:
    def __init__(self):
        self.connector = SqliteConnectionManager.get_connector()

    def __get_id_from_seq(self, query: str) -> int:
        with self.connector as cursor:
            cursor.execute(query)
            result = cursor.fetchone()[0]
            return result or 0

    def get_new_id_raw_images(self) -> int:
        query = "select seq from sqlite_sequence where name='cvision_images_raw'"
        return self.__get_id_from_seq(query)

    def get_new_id_analyzed_images(self) -> int:
        query = "select seq from sqlite_sequence where name='cvision_images_analyzed'"
        return self.__get_id_from_seq(query)

    def get_identifier_images_metadata(self) -> list:
        query = "select * from identifier_images"
        meta_data_images = []
        with self.connector as cursor:
            cursor.execute(query)
            for row in cursor.fetchall():
                meta_data_images.append(row)
        return meta_data_images
