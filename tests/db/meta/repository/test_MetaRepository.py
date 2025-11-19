import unittest
from unittest.mock import patch

from db.meta.repository.MetaRepository import MetaRepository
from db.meta.exceptions.DatabaseWriterError import DatabaseWriterError
from db.meta.exceptions.MetaRepositoryError import MetaRepositoryError


class TestMetaRepositoryIds(unittest.TestCase):

    @patch("db.meta.repository.MetaRepository.DatabaseReader")
    def test_get_new_id_raw_images_delegates_to_reader(self, mock_reader_cls):
        mock_reader = mock_reader_cls.return_value
        mock_reader.get_new_id_raw_images.return_value = 10

        repo = MetaRepository()
        result = repo.get_new_id_raw_images()

        self.assertEqual(result, 10)
        mock_reader.get_new_id_raw_images.assert_called_once()

    @patch("db.meta.repository.MetaRepository.DatabaseReader")
    def test_get_new_id_analyzed_images_delegates_to_reader(self, mock_reader_cls):
        mock_reader = mock_reader_cls.return_value
        mock_reader.get_new_id_analyzed_images.return_value = 5

        repo = MetaRepository()
        result = repo.get_new_id_analyzed_images()

        self.assertEqual(result, 5)
        mock_reader.get_new_id_analyzed_images.assert_called_once()


class TestMetaRepositoryInsertRaw(unittest.TestCase):

    @patch("db.meta.repository.MetaRepository.DatabaseWriter")
    @patch("db.meta.repository.MetaRepository.DatabaseReader")
    def test_insert_raw_image_metadata_success(self, mock_reader_cls, mock_writer_cls):
        mock_writer = mock_writer_cls.return_value
        mock_writer.insert_raw_image_metadata.return_value = (1, "img.png")

        repo = MetaRepository()

        class DummyRaw:
            pass

        metadata = DummyRaw()
        metadata.name = "img.png"
        metadata.format = "png"
        metadata.content_type = "image/png"
        metadata.bucket = "bucket"
        metadata.size = 123
        metadata.compressed = False
        metadata.compression_method = None

        result = repo.insert_raw_image_metadata(metadata)

        self.assertEqual(result, (1, "img.png"))
        mock_writer.insert_raw_image_metadata.assert_called_once_with(
            name="img.png",
            format="png",
            content_type="image/png",
            bucket="bucket",
            size=123,
            compressed=False,
            compression_method=None,
        )

    @patch("db.meta.repository.MetaRepository.DatabaseWriter")
    @patch("db.meta.repository.MetaRepository.DatabaseReader")
    def test_insert_raw_image_metadata_wraps_databasewritererror(
        self, mock_reader_cls, mock_writer_cls
    ):
        mock_writer = mock_writer_cls.return_value
        mock_writer.insert_raw_image_metadata.side_effect = DatabaseWriterError(
            exception=RuntimeError("db"), error_code=123
        )

        repo = MetaRepository()

        class DummyRaw:
            pass

        metadata = DummyRaw()
        metadata.name = "img.png"
        metadata.format = "png"
        metadata.content_type = "image/png"
        metadata.bucket = "bucket"
        metadata.size = 123
        metadata.compressed = False
        metadata.compression_method = None

        with self.assertRaises(MetaRepositoryError):
            repo.insert_raw_image_metadata(metadata)

    @patch("db.meta.repository.MetaRepository.DatabaseWriter")
    @patch("db.meta.repository.MetaRepository.DatabaseReader")
    def test_insert_raw_image_metadata_wraps_generic_exception(
        self, mock_reader_cls, mock_writer_cls
    ):
        mock_writer = mock_writer_cls.return_value
        mock_writer.insert_raw_image_metadata.side_effect = RuntimeError("boom")

        repo = MetaRepository()

        class DummyRaw:
            pass

        metadata = DummyRaw()
        metadata.name = "img.png"
        metadata.format = "png"
        metadata.content_type = "image/png"
        metadata.bucket = "bucket"
        metadata.size = 123
        metadata.compressed = False
        metadata.compression_method = None

        with self.assertRaises(MetaRepositoryError):
            repo.insert_raw_image_metadata(metadata)


class TestMetaRepositoryInsertAnalyzed(unittest.TestCase):

    @patch("db.meta.repository.MetaRepository.DatabaseWriter")
    @patch("db.meta.repository.MetaRepository.DatabaseReader")
    def test_insert_analyzed_image_metadata_success(
        self, mock_reader_cls, mock_writer_cls
    ):
        mock_writer = mock_writer_cls.return_value
        mock_writer.insert_analyzed_image_metadata.return_value = (2, "img.png")

        repo = MetaRepository()

        class DummyAnalyzed:
            pass

        metadata = DummyAnalyzed()
        metadata.name = "img.png"
        metadata.raw_image_id = 1
        metadata.format = "png"
        metadata.content_type = "image/png"
        metadata.bucket = "bucket"
        metadata.size = 123
        metadata.compressed = False
        metadata.compression_method = None
        metadata.sensor_type = "cam"
        metadata.category = "cat"
        metadata.quality = 0.9
        metadata.value = 42.0
        metadata.unit = "mm"

        result = repo.insert_analyzed_image_metadata(metadata)

        self.assertEqual(result, (2, "img.png"))
        mock_writer.insert_analyzed_image_metadata.assert_called_once_with(
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

    @patch("db.meta.repository.MetaRepository.DatabaseWriter")
    @patch("db.meta.repository.MetaRepository.DatabaseReader")
    def test_insert_analyzed_image_metadata_wraps_databasewritererror(
        self, mock_reader_cls, mock_writer_cls
    ):
        mock_writer = mock_writer_cls.return_value
        mock_writer.insert_analyzed_image_metadata.side_effect = DatabaseWriterError(
            exception=RuntimeError("db"), error_code=123
        )

        repo = MetaRepository()

        class DummyAnalyzed:
            pass

        metadata = DummyAnalyzed()
        metadata.name = "img.png"
        metadata.raw_image_id = 1
        metadata.format = "png"
        metadata.content_type = "image/png"
        metadata.bucket = "bucket"
        metadata.size = 123
        metadata.compressed = False
        metadata.compression_method = None
        metadata.sensor_type = "cam"
        metadata.category = "cat"
        metadata.quality = 0.9
        metadata.value = 42.0
        metadata.unit = "mm"

        with self.assertRaises(MetaRepositoryError):
            repo.insert_analyzed_image_metadata(metadata)

    @patch("db.meta.repository.MetaRepository.DatabaseWriter")
    @patch("db.meta.repository.MetaRepository.DatabaseReader")
    def test_insert_analyzed_image_metadata_wraps_generic_exception(
        self, mock_reader_cls, mock_writer_cls
    ):
        mock_writer = mock_writer_cls.return_value
        mock_writer.insert_analyzed_image_metadata.side_effect = RuntimeError("boom")

        repo = MetaRepository()

        class DummyAnalyzed:
            pass

        metadata = DummyAnalyzed()
        metadata.name = "img.png"
        metadata.raw_image_id = 1
        metadata.format = "png"
        metadata.content_type = "image/png"
        metadata.bucket = "bucket"
        metadata.size = 123
        metadata.compressed = False
        metadata.compression_method = None
        metadata.sensor_type = "cam"
        metadata.category = "cat"
        metadata.quality = 0.9
        metadata.value = 42.0
        metadata.unit = "mm"

        with self.assertRaises(MetaRepositoryError):
            repo.insert_analyzed_image_metadata(metadata)


if __name__ == "__main__":
    unittest.main()
