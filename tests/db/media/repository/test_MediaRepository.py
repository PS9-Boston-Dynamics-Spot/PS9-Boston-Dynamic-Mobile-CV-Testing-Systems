import unittest
from unittest.mock import patch, MagicMock

from db.media.repository.MediaRepository import MediaRepository
from db.media.exceptions.BucketInitializerError import BucketInitializerError
from db.media.exceptions.MinioWriterError import MinioWriterError
from db.media.exceptions.MediaRepositoryError import MediaRepositoryError


class TestMediaRepositoryInitializeBucket(unittest.TestCase):

    @patch("db.media.repository.MediaRepository.MinioBucketInitializer")
    def test_initialize_bucket_success(self, mock_initializer_cls):
        mock_initializer = mock_initializer_cls.return_value
        mock_initializer.initalize_bucket.return_value = "bucket"

        repo = MediaRepository(bucket_name="bucket")
        # private Methode via Name-Mangling
        result = repo._MediaRepository__initialize_bucket()

        self.assertEqual(result, "bucket")
        mock_initializer_cls.assert_called_once_with("bucket")
        mock_initializer.initalize_bucket.assert_called_once()

    @patch("db.media.repository.MediaRepository.MinioBucketInitializer")
    def test_initialize_bucket_wraps_bucketinitializererror(self, mock_initializer_cls):
        mock_initializer = mock_initializer_cls.return_value
        mock_initializer.initalize_bucket.side_effect = BucketInitializerError(
            exception=ValueError("x"), error_code=123
        )

        repo = MediaRepository("bucket")

        with self.assertRaises(MediaRepositoryError):
            repo._MediaRepository__initialize_bucket()

    @patch("db.media.repository.MediaRepository.MinioBucketInitializer")
    def test_initialize_bucket_wraps_generic_exception(self, mock_initializer_cls):
        mock_initializer = mock_initializer_cls.return_value
        mock_initializer.initalize_bucket.side_effect = RuntimeError("boom")

        repo = MediaRepository("bucket")

        with self.assertRaises(MediaRepositoryError):
            repo._MediaRepository__initialize_bucket()


class TestMediaRepositoryPutMedia(unittest.TestCase):

    @patch("db.media.repository.MediaRepository.MinioBucketInitializer")
    @patch("db.media.repository.MediaRepository.MinioWriter")
    def test_put_media_success(self, mock_writer_cls, mock_initializer_cls):
        mock_initializer = mock_initializer_cls.return_value
        mock_initializer.initalize_bucket.return_value = "bucket"

        mock_writer = MagicMock()
        mock_writer_cls.return_value = mock_writer
        mock_writer.__enter__.return_value = mock_writer

        repo = MediaRepository(bucket_name="bucket")

        repo.put_media(
            object_name="obj",
            image_data=b"data",
            content_type="image/png",
        )

        mock_initializer_cls.assert_called_once_with("bucket")
        mock_writer_cls.assert_called_once_with("bucket")
        mock_writer.put_media.assert_called_once_with(
            object_name="obj",
            image_data=b"data",
            content_type="image/png",
        )

    @patch("db.media.repository.MediaRepository.MinioBucketInitializer")
    @patch("db.media.repository.MediaRepository.MinioWriter")
    def test_put_media_wraps_miniowritererror(
        self, mock_writer_cls, mock_initializer_cls
    ):
        mock_initializer = mock_initializer_cls.return_value
        mock_initializer.initalize_bucket.return_value = "bucket"

        mock_writer = MagicMock()
        mock_writer.__enter__.return_value = mock_writer
        mock_writer.put_media.side_effect = MinioWriterError(
            exception=ValueError("x"), error_code=123
        )
        mock_writer_cls.return_value = mock_writer

        repo = MediaRepository("bucket")

        with self.assertRaises(MediaRepositoryError):
            repo.put_media(
                object_name="obj",
                image_data=b"data",
                content_type="image/png",
            )

    @patch("db.media.repository.MediaRepository.MinioBucketInitializer")
    @patch("db.media.repository.MediaRepository.MinioWriter")
    def test_put_media_wraps_generic_exception(
        self, mock_writer_cls, mock_initializer_cls
    ):
        mock_initializer = mock_initializer_cls.return_value
        mock_initializer.initalize_bucket.return_value = "bucket"

        mock_writer = MagicMock()
        mock_writer.__enter__.return_value = mock_writer
        mock_writer.put_media.side_effect = RuntimeError("boom")
        mock_writer_cls.return_value = mock_writer

        repo = MediaRepository("bucket")

        with self.assertRaises(MediaRepositoryError):
            repo.put_media(
                object_name="obj",
                image_data=b"data",
                content_type="image/png",
            )


if __name__ == "__main__":
    unittest.main()
