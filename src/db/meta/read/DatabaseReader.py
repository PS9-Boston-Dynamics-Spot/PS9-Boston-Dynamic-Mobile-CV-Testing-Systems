from db.meta.connector.SqliteConnector import SqliteConnector


class DatabaseReader:
    def __init__(self):
        self.connector = SqliteConnector()

    def get_new_id(self) -> int:
        query = "SELECT MAX(id) FROM cvision_images_raw;"
        with self.connector as cursor:
            cursor.execute(query)
            result = cursor.fetchone()[0]
            return (result or 0) + 1
