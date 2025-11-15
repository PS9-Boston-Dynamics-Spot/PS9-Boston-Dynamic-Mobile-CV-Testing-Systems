import io
import unittest
from unittest.mock import patch, MagicMock

from minio.error import S3Error
from db.media.write.MinioWriter import MinioWriter
from db.media.exceptions.MinioWriterError import MinioWriterError


class TestMinioWriterPrivateHelpers(unittest.TestCase):

    @patch("db.media.write.MinioWriter.MinioConnector.__init__")
    def setUp(self, mock_init):
        mock_init.return_value = None
        self.writer = MinioWriter(bucket_name="test-bucket")
        self.writer.client = MagicMock()

    def test_get_bytes_length(self):
        image_data = b"12345"
        length = self.writer._MinioWriter__get_bytes_length(image_data)
        self.assertEqual(length, 5)

    def test_check_object_already_exists_true(self):
        # Kein Fehler -> True
        self.writer.client.stat_object.return_value = object()

        exists = self.writer._MinioWriter__check_object_already_exists("obj")

        self.assertTrue(exists)
        self.writer.client.stat_object.assert_called_once_with(
            bucket_name="test-bucket", object_name="obj"
        )

        def test_check_object_already_exists_false_on_nosuchkey(self):
            # Dummy-Subklasse von S3Error mit nur einem code-Attribut
            class DummyS3Error(S3Error):
                def __init__(self, code):
                    self.code = code

            def raise_err(*args, **kwargs):
                raise DummyS3Error("NoSuchKey")

            self.writer.client.stat_object.side_effect = raise_err

            exists = self.writer._MinioWriter__check_object_already_exists("obj")

            self.assertFalse(exists)

        def test_check_object_already_exists_raises_on_other_s3error(self):
            class DummyS3Error(S3Error):
                def __init__(self, code):
                    self.code = code

            def raise_err(*args, **kwargs):
                raise DummyS3Error("SomeOtherCode")

            self.writer.client.stat_object.side_effect = raise_err

            with self.assertRaises(MinioWriterError):
                self.writer._MinioWriter__check_object_already_exists("obj")


class TestMinioWriterPutMedia(unittest.TestCase):

    @patch("db.media.write.MinioWriter.MinioConnector.__init__")
    def setUp(self, mock_init):
        mock_init.return_value = None
        self.writer = MinioWriter(bucket_name="test-bucket")
        self.writer.client = MagicMock()

    @patch(
        "db.media.write.MinioWriter.MinioWriter._MinioWriter__check_object_already_exists"
    )
    def test_put_media_raises_if_object_exists(self, mock_check_exists):
        mock_check_exists.return_value = True

        with self.assertRaises(MinioWriterError):
            self.writer.put_media(
                object_name="obj",
                image_data=b"data",
                content_type="image/png",
            )

    @patch(
        "db.media.write.MinioWriter.MinioWriter._MinioWriter__check_object_already_exists"
    )
    def test_put_media_puts_object_if_not_exists(self, mock_check_exists):
        mock_check_exists.return_value = False

        image_data = b"abcdef"
        self.writer.put_media(
            object_name="obj",
            image_data=image_data,
            content_type="image/png",
        )

        # put_object wurde mit korrekt berechneter Länge aufgerufen
        self.writer.client.put_object.assert_called_once()
        _, kwargs = self.writer.client.put_object.call_args
        self.assertEqual(kwargs["bucket_name"], "test-bucket")
        self.assertEqual(kwargs["object_name"], "obj")
        self.assertIsInstance(kwargs["data"], io.BytesIO)
        self.assertEqual(kwargs["length"], len(image_data))
        self.assertEqual(kwargs["content_type"], "image/png")

    @patch(
        "db.media.write.MinioWriter.MinioWriter._MinioWriter__check_object_already_exists"
    )
    def test_put_media_wraps_exceptions_in_miniowritererror(self, mock_check_exists):
        mock_check_exists.return_value = False
        self.writer.client.put_object.side_effect = RuntimeError("boom")

        with self.assertRaises(MinioWriterError):
            self.writer.put_media(
                object_name="obj",
                image_data=b"data",
                content_type="image/png",
            )


if __name__ == "__main__":
    unittest.main()
