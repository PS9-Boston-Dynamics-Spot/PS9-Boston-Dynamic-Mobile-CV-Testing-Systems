import unittest
from unittest.mock import patch, MagicMock

from db.meta.manager.SqliteConnectionManager import SqliteConnectionManager


class TestSqliteConnectionManager(unittest.TestCase):

    def setUp(self):
        SqliteConnectionManager._instance = None

    @patch("db.meta.manager.SqliteConnectionManager.SqliteConnector")
    def test_get_connector_returns_singleton(self, mock_connector_cls):
        connector_instance = MagicMock()
        mock_connector_cls.return_value = connector_instance

        first = SqliteConnectionManager.get_connector()
        second = SqliteConnectionManager.get_connector()

        mock_connector_cls.assert_called_once()
        self.assertIs(first, connector_instance)
        self.assertIs(second, connector_instance)

    @patch("db.meta.manager.SqliteConnectionManager.SqliteConnector")
    def test_close_calls_close_and_resets_instance(self, mock_connector_cls):
        connector_instance = MagicMock()
        mock_connector_cls.return_value = connector_instance

        SqliteConnectionManager._instance = SqliteConnectionManager.get_connector()
        SqliteConnectionManager.close()

        connector_instance.close.assert_called_once()
        self.assertIsNone(SqliteConnectionManager._instance)

    def test_close_without_instance_does_nothing(self):
        SqliteConnectionManager._instance = None
        SqliteConnectionManager.close()
        self.assertIsNone(SqliteConnectionManager._instance)


if __name__ == "__main__":
    unittest.main()
