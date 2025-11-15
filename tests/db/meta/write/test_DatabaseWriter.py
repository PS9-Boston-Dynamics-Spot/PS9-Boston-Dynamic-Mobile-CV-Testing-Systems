import unittest
from unittest.mock import patch, MagicMock

from sqlite3 import IntegrityError, OperationalError, DatabaseError

from db.meta.write.DatabaseWriter import DatabaseWriter
from db.meta.exceptions.SqliteConnectionError import SqliteConnectionError
from db.meta.exceptions.DatabaseWriterError import DatabaseWriterError


class DatabaseWriterTestBase(unittest.TestCase):

    def _make_writer_with_cursor(self):
        with patch("db.meta.write.DatabaseWriter.SqliteConnectionManager") as mock_mgr:
            mock_connector = MagicMock()
            mock_cursor = MagicMock()
            mock_mgr.get_connector.return_value = mock_connector
            mock_connector.__enter__.return_value = mock_cursor
            mock_connector.__exit__.return_value = None

            writer = DatabaseWriter()

        return writer, mock_connector, mock_cursor


class TestInsertRawImageMetadata(DatabaseWriterTestBase):

    def test_insert_raw_image_metadata_success(self):
        writer, connector, cursor = self._make_writer_with_cursor()
        cursor.lastrowid = 42

        result = writer.insert_raw_image_metadata(
            name="img.png",
            format="png",
            content_type="image/png",
            bucket="bucket",
            size=123,
            compressed=False,
            compression_method=None,
        )

        self.assertEqual(result, (42, "img.png"))
        cursor.execute.assert_called_once()
        args, kwargs = cursor.execute.call_args
        # Statement selbst müssen wir nicht komplett prüfen, nur dass Parameter stimmen
        self.assertIn("INSERT INTO cvision_images_raw", args[0])
        self.assertEqual(
            args[1],
            ("img.png", "png", "image/png", "bucket", 123, False, None),
        )

    def test_insert_raw_image_metadata_integrity_error(self):
        writer, connector, cursor = self._make_writer_with_cursor()
        cursor.execute.side_effect = IntegrityError("constraint")

        with self.assertRaises(DatabaseWriterError):
            writer.insert_raw_image_metadata(
                "img.png", "png", "image/png", "bucket", 123, False, None
            )

    def test_insert_raw_image_metadata_operational_error(self):
        writer, connector, cursor = self._make_writer_with_cursor()
        cursor.execute.side_effect = OperationalError("operational")

        with self.assertRaises(DatabaseWriterError):
            writer.insert_raw_image_metadata(
                "img.png", "png", "image/png", "bucket", 123, False, None
            )

    def test_insert_raw_image_metadata_database_error(self):
        writer, connector, cursor = self._make_writer_with_cursor()
        cursor.execute.side_effect = DatabaseError("db")

        with self.assertRaises(DatabaseWriterError):
            writer.insert_raw_image_metadata(
                "img.png", "png", "image/png", "bucket", 123, False, None
            )

    def test_insert_raw_image_metadata_sqlite_connection_error(self):
        writer, connector, cursor = self._make_writer_with_cursor()
        # Fehler beim Betreten des Kontextmanagers simulieren
        connector.__enter__.side_effect = SqliteConnectionError(
            exception=RuntimeError("conn"), error_code=123
        )

        with self.assertRaises(DatabaseWriterError):
            writer.insert_raw_image_metadata(
                "img.png", "png", "image/png", "bucket", 123, False, None
            )

    def test_insert_raw_image_metadata_generic_exception(self):
        writer, connector, cursor = self._make_writer_with_cursor()
        cursor.execute.side_effect = RuntimeError("boom")

        with self.assertRaises(DatabaseWriterError):
            writer.insert_raw_image_metadata(
                "img.png", "png", "image/png", "bucket", 123, False, None
            )


class TestInsertAnalyzedImageMetadata(DatabaseWriterTestBase):

    def test_insert_analyzed_image_metadata_success(self):
        writer, connector, cursor = self._make_writer_with_cursor()
        cursor.lastrowid = 7

        result = writer.insert_analyzed_image_metadata(
            name="img.png",
            raw_image_id=1,
            format="png",
            content_type="image/png",
            bucket="bucket",
            size=123,
            compressed=False,
            compression_method=None,
            sensor_type="cam",
            category="cat",
            quality=0.9,
            value=42.0,
            unit="mm",
        )

        self.assertEqual(result, (7, "img.png"))
        cursor.execute.assert_called_once()
        args, kwargs = cursor.execute.call_args
        self.assertIn("INSERT INTO cvision_images_analyzed", args[0])
        self.assertEqual(
            args[1],
            (
                1,
                "img.png",
                "png",
                "image/png",
                "bucket",
                123,
                False,
                None,
                "cam",
                "cat",
                0.9,
                42.0,
                "mm",
            ),
        )

    def test_insert_analyzed_image_metadata_integrity_error(self):
        writer, connector, cursor = self._make_writer_with_cursor()
        cursor.execute.side_effect = IntegrityError("constraint")

        with self.assertRaises(DatabaseWriterError):
            writer.insert_analyzed_image_metadata(
                "img.png",
                1,
                "png",
                "image/png",
                "bucket",
                123,
                False,
                None,
                "cam",
                "cat",
                0.9,
                42.0,
                "mm",
            )

    def test_insert_analyzed_image_metadata_operational_error(self):
        writer, connector, cursor = self._make_writer_with_cursor()
        cursor.execute.side_effect = OperationalError("op")

        with self.assertRaises(DatabaseWriterError):
            writer.insert_analyzed_image_metadata(
                "img.png",
                1,
                "png",
                "image/png",
                "bucket",
                123,
                False,
                None,
                "cam",
                "cat",
                0.9,
                42.0,
                "mm",
            )

    def test_insert_analyzed_image_metadata_database_error(self):
        writer, connector, cursor = self._make_writer_with_cursor()
        cursor.execute.side_effect = DatabaseError("db")

        with self.assertRaises(DatabaseWriterError):
            writer.insert_analyzed_image_metadata(
                "img.png",
                1,
                "png",
                "image/png",
                "bucket",
                123,
                False,
                None,
                "cam",
                "cat",
                0.9,
                42.0,
                "mm",
            )

    def test_insert_analyzed_image_metadata_sqlite_connection_error(self):
        writer, connector, cursor = self._make_writer_with_cursor()
        connector.__enter__.side_effect = SqliteConnectionError(
            exception=RuntimeError("conn"), error_code=123
        )

        with self.assertRaises(DatabaseWriterError):
            writer.insert_analyzed_image_metadata(
                "img.png",
                1,
                "png",
                "image/png",
                "bucket",
                123,
                False,
                None,
                "cam",
                "cat",
                0.9,
                42.0,
                "mm",
            )

    def test_insert_analyzed_image_metadata_generic_exception(self):
        writer, connector, cursor = self._make_writer_with_cursor()
        cursor.execute.side_effect = RuntimeError("boom")

        with self.assertRaises(DatabaseWriterError):
            writer.insert_analyzed_image_metadata(
                "img.png",
                1,
                "png",
                "image/png",
                "bucket",
                123,
                False,
                None,
                "cam",
                "cat",
                0.9,
                42.0,
                "mm",
            )


if __name__ == "__main__":
    unittest.main()
