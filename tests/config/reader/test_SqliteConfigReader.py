import unittest
from unittest.mock import patch
from configs.reader.SqliteConfigReader import SqliteConfigReader
from configs.enum.ConfigEnum import SQLITE_KEYS


class TestSqliteConfigReader(unittest.TestCase):

    def setUp(self):
        self.mock_config = {
            SQLITE_KEYS.SQLITE: {
                SQLITE_KEYS.DATABASE: "mydb.sqlite",
                SQLITE_KEYS.TIMEOUT: 30,
                SQLITE_KEYS.DETECT_TYPES: 1,
                SQLITE_KEYS.ISOLATION_LEVEL: "DEFERRED",
                SQLITE_KEYS.CHECK_SAME_THREAD: True,
                SQLITE_KEYS.CACHED_STATEMENTS: 100,
                SQLITE_KEYS.URI: False,
            }
        }

    @patch.object(SqliteConfigReader, "load_config")
    def test_sqlite_edge_none_section(self, mock_load_config):
        mock_load_config.return_value = {SQLITE_KEYS.SQLITE: None}
        reader = SqliteConfigReader()
        self.assertIsNone(reader.getDatabase())
        self.assertIsNone(reader.getTimeout())
        self.assertIsNone(reader.getDetectTypes())

    @patch.object(SqliteConfigReader, "load_config")
    def test_sqlite_edge_wrong_type_section(self, mock_load_config):
        mock_load_config.return_value = {SQLITE_KEYS.SQLITE: 12345}
        reader = SqliteConfigReader()
        self.assertIsNone(reader.getDatabase())
        self.assertIsNone(reader.getTimeout())
        self.assertIsNone(reader.getDetectTypes())

    @patch.object(SqliteConfigReader, "load_config")
    def test_sqlite_missing_section(self, mock_load_config):
        mock_load_config.return_value = {}
        reader = SqliteConfigReader()
        self.assertIsNone(reader.getDatabase())
        self.assertIsNone(reader.getTimeout())
        self.assertIsNone(reader.getDetectTypes())

    @patch.object(SqliteConfigReader, "load_config")
    def test_sqlite_partial_config(self, mock_load_config):
        partial_config = {SQLITE_KEYS.SQLITE: {SQLITE_KEYS.DATABASE: "mydb.sqlite"}}
        mock_load_config.return_value = partial_config
        reader = SqliteConfigReader()
        self.assertEqual(reader.getDatabase(), "mydb.sqlite")
        self.assertIsNone(reader.getTimeout())
        self.assertIsNone(reader.getDetectTypes())

    @patch.object(SqliteConfigReader, "load_config")
    def test_sqlite_full_config(self, mock_load_config):
        mock_load_config.return_value = self.mock_config
        reader = SqliteConfigReader()
        self.assertEqual(reader.getDatabase(), "mydb.sqlite")
        self.assertEqual(reader.getTimeout(), 30)
        self.assertEqual(reader.getDetectTypes(), 1)
        self.assertEqual(reader.getIsolationLevel(), "DEFERRED")
        self.assertEqual(reader.getCheckSameThread(), True)
        self.assertEqual(reader.getCachedStatements(), 100)
        self.assertEqual(reader.getUri(), False)

    @patch.object(SqliteConfigReader, "load_config")
    def test_sqlite_empty_string_values(self, mock_load_config):
        mock_load_config.return_value = {
            SQLITE_KEYS.SQLITE: {
                SQLITE_KEYS.DATABASE: "",
                SQLITE_KEYS.ISOLATION_LEVEL: "",
            }
        }
        reader = SqliteConfigReader()
        self.assertEqual(reader.getDatabase(), "")
        self.assertEqual(reader.getIsolationLevel(), "")

    @patch.object(SqliteConfigReader, "load_config")
    def test_sqlite_negative_numbers(self, mock_load_config):
        mock_load_config.return_value = {
            SQLITE_KEYS.SQLITE: {
                SQLITE_KEYS.TIMEOUT: -1,
                SQLITE_KEYS.CACHED_STATEMENTS: -100,
            }
        }
        reader = SqliteConfigReader()
        self.assertEqual(reader.getTimeout(), -1)
        self.assertEqual(reader.getCachedStatements(), -100)

    @patch.object(SqliteConfigReader, "load_config")
    def test_sqlite_wrong_bool_type(self, mock_load_config):
        mock_load_config.return_value = {
            SQLITE_KEYS.SQLITE: {SQLITE_KEYS.CHECK_SAME_THREAD: "not_a_bool"}
        }
        reader = SqliteConfigReader()
        self.assertEqual(reader.getCheckSameThread(), "not_a_bool")
