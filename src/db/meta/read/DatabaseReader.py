from db.meta.connector.SqliteConnector import SqliteConnector
from typing import Any, Dict, List, Optional

class DatabaseReader:
    def __init__(self):
        self.connector = SqliteConnector()


    def get_new_id(self) -> int:
        query = "SELECT MAX(id) FROM cvision_images_raw;"
        with self.connector as cursor:
            cursor.execute(query)
            result = cursor.fetchone()[0]
            return (result or 0) + 1

    def _fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        with self.connector as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_all_raw_images(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM cvision_images_raw ORDER BY timestamp DESC;"
        return self._fetch_all(query)

    def get_raw_image_by_id(self, raw_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM cvision_images_raw WHERE id = ?;"
        rows = self._fetch_all(query, (raw_id,))
        return rows[0] if rows else None

    def get_raw_image_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM cvision_images_raw WHERE name = ?;"
        rows = self._fetch_all(query, (name,))
        return rows[0] if rows else None
    
    def get_all_analyzed_images(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM cvision_images_analyzed ORDER BY timestamp DESC;"
        return self._fetch_all(query)

    def get_analyzed_by_category(self, category: str) -> List[Dict[str, Any]]:
        query = "SELECT * FROM cvision_images_analyzed WHERE category = ? ORDER BY timestamp DESC;"
        return self._fetch_all(query, (category,))

    def get_analyzed_for_raw_id(self, raw_id: int) -> List[Dict[str, Any]]:
        query = "SELECT * FROM cvision_images_analyzed WHERE raw_image_id = ? ORDER BY timestamp DESC;"
        return self._fetch_all(query, (raw_id,))