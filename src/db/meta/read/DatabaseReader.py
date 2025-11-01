from db.meta.manager.SqliteConnectionManager import SqliteConnectionManager


class DatabaseReader:
    def __init__(self):
        self.connector = SqliteConnectionManager.get_connector()

    def get_new_id_raw_images(self) -> int:
        query = "SELECT MAX(id) FROM cvision_images_raw;"
        with self.connector as cursor:
            cursor.execute(query)
            result = cursor.fetchone()[0]
            return (result or 0) + 1
        
    def get_new_id_analyzed_images(self) -> int:
        query = "SELECT MAX(id) FROM cvision_images_analyzed;"
        with self.connector as cursor:
            cursor.execute(query)
            result = cursor.fetchone()[0]
            return (result or 0) + 1
