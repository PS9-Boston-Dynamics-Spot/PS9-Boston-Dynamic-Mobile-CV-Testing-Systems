import unittest
from unittest.mock import patch, MagicMock

from db.meta.read.DatabaseReader import DatabaseReader


class TestDatabaseReader(unittest.TestCase):

    @patch("db.meta.read.DatabaseReader.SqliteConnectionManager")
    def test_get_new_id_raw_images_with_existing_seq(self, mock_manager_cls):
        mock_connector = MagicMock()
        mock_cursor = MagicMock()
        mock_manager_cls.get_connector.return_value = mock_connector
        mock_connector.__enter__.return_value = mock_cursor
        mock_connector.__exit__.return_value = None

        mock_cursor.fetchone.return_value = (5,)

        reader = DatabaseReader()
        new_id = reader.get_new_id_raw_images()

        self.assertEqual(new_id, 6)
        mock_cursor.execute.assert_called_once_with(
            "select seq from sqlite_sequence where name='cvision_images_raw'"
        )

    @patch("db.meta.read.DatabaseReader.SqliteConnectionManager")
    def test_get_new_id_raw_images_when_none(self, mock_manager_cls):
        mock_connector = MagicMock()
        mock_cursor = MagicMock()
        mock_manager_cls.get_connector.return_value = mock_connector
        mock_connector.__enter__.return_value = mock_cursor
        mock_connector.__exit__.return_value = None

        mock_cursor.fetchone.return_value = (None,)

        reader = DatabaseReader()
        new_id = reader.get_new_id_raw_images()

        self.assertEqual(new_id, 1)

    @patch("db.meta.read.DatabaseReader.SqliteConnectionManager")
    def test_get_new_id_analyzed_images_with_existing_seq(self, mock_manager_cls):
        mock_connector = MagicMock()
        mock_cursor = MagicMock()
        mock_manager_cls.get_connector.return_value = mock_connector
        mock_connector.__enter__.return_value = mock_cursor
        mock_connector.__exit__.return_value = None

        mock_cursor.fetchone.return_value = (10,)

        reader = DatabaseReader()
        new_id = reader.get_new_id_analyzed_images()

        self.assertEqual(new_id, 11)
        mock_cursor.execute.assert_called_once_with(
            "select seq from sqlite_sequence where name='cvision_images_analyzed'"
        )

    @patch("db.meta.read.DatabaseReader.SqliteConnectionManager")
    def test_get_new_id_analyzed_images_when_none(self, mock_manager_cls):
        mock_connector = MagicMock()
        mock_cursor = MagicMock()
        mock_manager_cls.get_connector.return_value = mock_connector
        mock_connector.__enter__.return_value = mock_cursor
        mock_connector.__exit__.return_value = None

        mock_cursor.fetchone.return_value = (None,)

        reader = DatabaseReader()
        new_id = reader.get_new_id_analyzed_images()

        self.assertEqual(new_id, 1)


if __name__ == "__main__":
    unittest.main()
