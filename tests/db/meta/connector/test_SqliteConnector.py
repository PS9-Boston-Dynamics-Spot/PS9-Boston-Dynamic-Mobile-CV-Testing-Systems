import unittest
from unittest.mock import patch, MagicMock

from db.meta.connector.SqliteConnector import SqliteConnector
from db.meta.exceptions.SqliteConnectionError import SqliteConnectionError


class TestSqliteConnectorInit(unittest.TestCase):

    def setUp(self):
        # shared connection immer zurücksetzen, damit Tests unabhängig sind
        SqliteConnector._shared_connection = None

    @patch("db.meta.connector.SqliteConnector.SqliteConfigReader")
    @patch("db.meta.connector.SqliteConnector.connect")
    def test_init_creates_shared_connection_with_valid_config(
        self, mock_connect, mock_config_cls
    ):
        mock_config = mock_config_cls.return_value
        mock_config.getIsolationLevel.return_value = "DEFERRED"
        mock_config.getDatabase.return_value = "test.db"
        mock_config.getTimeout.return_value = 5.0
        mock_config.getDetectTypes.return_value = 0
        mock_config.getCheckSameThread.return_value = True
        mock_config.getCachedStatements.return_value = 100
        mock_config.getUri.return_value = False

        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        connector = SqliteConnector()

        mock_connect.assert_called_once_with(
            database="test.db",
            timeout=5.0,
            detect_types=0,
            isolation_level="DEFERRED",
            check_same_thread=True,
            cached_statements=100,
            uri=False,
        )
        self.assertIs(SqliteConnector._shared_connection, mock_connection)
        self.assertIs(connector.connection, mock_connection)

    @patch("db.meta.connector.SqliteConnector.SqliteConfigReader")
    def test_init_raises_on_invalid_isolation_level(self, mock_config_cls):
        mock_config = mock_config_cls.return_value
        mock_config.getIsolationLevel.return_value = "INVALID"

        with self.assertRaises(SqliteConnectionError):
            SqliteConnector()

    @patch("db.meta.connector.SqliteConnector.SqliteConfigReader")
    @patch("db.meta.connector.SqliteConnector.connect")
    def test_ensure_connection_reinitializes_when_shared_is_none(
        self, mock_connect, mock_config_cls
    ):
        # shared connection zunächst manuell auf None
        SqliteConnector._shared_connection = None

        mock_config = mock_config_cls.return_value
        mock_config.getIsolationLevel.return_value = None
        mock_config.getDatabase.return_value = "test.db"
        mock_config.getTimeout.return_value = 5.0
        mock_config.getDetectTypes.return_value = 0
        mock_config.getCheckSameThread.return_value = True
        mock_config.getCachedStatements.return_value = 100
        mock_config.getUri.return_value = False

        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        connector = SqliteConnector()
        # shared connection ist jetzt gesetzt
        SqliteConnector._shared_connection = None  # simuliert Verlust der Verbindung

        # _ensure_connection soll neu initialisieren
        connector._ensure_connection()
        self.assertIs(SqliteConnector._shared_connection, mock_connection)
        self.assertIs(connector.connection, mock_connection)


class TestSqliteConnectorContextManager(unittest.TestCase):

    def setUp(self):
        SqliteConnector._shared_connection = None

    @patch("db.meta.connector.SqliteConnector.SqliteConfigReader")
    @patch("db.meta.connector.SqliteConnector.connect")
    def test_context_manager_commits_and_closes_cursor(
        self, mock_connect, mock_config_cls
    ):
        mock_config = mock_config_cls.return_value
        mock_config.getIsolationLevel.return_value = None
        mock_config.getDatabase.return_value = "test.db"
        mock_config.getTimeout.return_value = 5.0
        mock_config.getDetectTypes.return_value = 0
        mock_config.getCheckSameThread.return_value = True
        mock_config.getCachedStatements.return_value = 100
        mock_config.getUri.return_value = False

        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        connector = SqliteConnector()

        with connector as cursor:
            self.assertIs(cursor, mock_cursor)

        mock_connection.commit.assert_called_once()
        mock_connection.rollback.assert_not_called()
        mock_cursor.close.assert_called_once()

    @patch("db.meta.connector.SqliteConnector.SqliteConfigReader")
    @patch("db.meta.connector.SqliteConnector.connect")
    def test_context_manager_rolls_back_on_exception(
        self, mock_connect, mock_config_cls
    ):
        mock_config = mock_config_cls.return_value
        mock_config.getIsolationLevel.return_value = None
        mock_config.getDatabase.return_value = "test.db"
        mock_config.getTimeout.return_value = 5.0
        mock_config.getDetectTypes.return_value = 0
        mock_config.getCheckSameThread.return_value = True
        mock_config.getCachedStatements.return_value = 100
        mock_config.getUri.return_value = False

        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        connector = SqliteConnector()

        with self.assertRaises(RuntimeError):
            with connector as cursor:
                self.assertIs(cursor, mock_cursor)
                raise RuntimeError("boom")

        mock_connection.rollback.assert_called_once()
        mock_connection.commit.assert_not_called()
        mock_cursor.close.assert_called_once()


class TestSqliteConnectorClose(unittest.TestCase):

    def setUp(self):
        SqliteConnector._shared_connection = None

    @patch("db.meta.connector.SqliteConnector.SqliteConfigReader")
    @patch("db.meta.connector.SqliteConnector.connect")
    def test_close_closes_shared_connection_and_resets(
        self, mock_connect, mock_config_cls
    ):
        mock_config = mock_config_cls.return_value
        mock_config.getIsolationLevel.return_value = None
        mock_config.getDatabase.return_value = "test.db"
        mock_config.getTimeout.return_value = 5.0
        mock_config.getDetectTypes.return_value = 0
        mock_config.getCheckSameThread.return_value = True
        mock_config.getCachedStatements.return_value = 100
        mock_config.getUri.return_value = False

        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        SqliteConnector()  # initialisiert shared connection
        self.assertIsNotNone(SqliteConnector._shared_connection)

        SqliteConnector.close()

        mock_connection.close.assert_called_once()
        self.assertIsNone(SqliteConnector._shared_connection)


if __name__ == "__main__":
    unittest.main()
