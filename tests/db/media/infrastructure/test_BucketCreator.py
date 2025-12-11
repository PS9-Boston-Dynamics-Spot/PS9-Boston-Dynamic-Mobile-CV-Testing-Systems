import unittest
from unittest.mock import patch, MagicMock

from db.media.infrastructure.BucketCreator import BucketCreator
from db.media.exceptions.BucketCreatorError import BucketCreatorError


class TestBucketCreator(unittest.TestCase):

    @patch("db.media.infrastructure.BucketCreator.MinioConnector.__init__")
    @patch("db.media.infrastructure.BucketCreator.MinioConnector._connect")
    def setUp(self, mock_connect, mock_init):
        mock_init.return_value = None
        mock_connect.return_value = None
        self.creator = BucketCreator()

    @patch("db.media.infrastructure.BucketCreator.BucketCreator.__enter__")
    @patch("db.media.infrastructure.BucketCreator.BucketCreator.__exit__")
    def test_bucket_exists_true(self, mock_exit, mock_enter):
        client = MagicMock()
        client.bucket_exists.return_value = True
        mock_enter.return_value = client

        result = self.creator.bucket_exists("test-bucket")
        self.assertTrue(result)
        client.bucket_exists.assert_called_once_with("test-bucket")

    @patch("db.media.infrastructure.BucketCreator.BucketCreator.__enter__")
    @patch("db.media.infrastructure.BucketCreator.BucketCreator.__exit__")
    def test_bucket_exists_false(self, mock_exit, mock_enter):
        client = MagicMock()
        client.bucket_exists.return_value = False
        mock_enter.return_value = client

        result = self.creator.bucket_exists("test-bucket")
        self.assertFalse(result)

    @patch("db.media.infrastructure.BucketCreator.BucketCreator.__enter__")
    @patch("db.media.infrastructure.BucketCreator.BucketCreator.__exit__")
    def test_bucket_exists_raises_bucketcreatorerror(self, mock_exit, mock_enter):
        mock_enter.side_effect = RuntimeError("some error")

        with self.assertRaises(BucketCreatorError):
            self.creator.bucket_exists("test-bucket")

    @patch("db.media.infrastructure.BucketCreator.BucketCreator.__enter__")
    @patch("db.media.infrastructure.BucketCreator.BucketCreator.__exit__")
    def test_ensure_bucket_creates_when_not_exists(self, mock_exit, mock_enter):
        client = MagicMock()
        client.bucket_exists.return_value = False
        mock_enter.return_value = client

        bucket_name = self.creator.ensure_bucket("test-bucket")

        self.assertEqual(bucket_name, "test-bucket")
        client.bucket_exists.assert_called_once_with("test-bucket")
        client.make_bucket.assert_called_once_with("test-bucket")

    @patch("db.media.infrastructure.BucketCreator.BucketCreator.__enter__")
    @patch("db.media.infrastructure.BucketCreator.BucketCreator.__exit__")
    def test_ensure_bucket_does_not_create_when_exists(self, mock_exit, mock_enter):
        client = MagicMock()
        client.bucket_exists.return_value = True
        mock_enter.return_value = client

        bucket_name = self.creator.ensure_bucket("test-bucket")

        self.assertEqual(bucket_name, "test-bucket")
        client.bucket_exists.assert_called_once_with("test-bucket")
        client.make_bucket.assert_not_called()

    @patch("db.media.infrastructure.BucketCreator.BucketCreator.__exit__")
    @patch("db.media.infrastructure.BucketCreator.BucketCreator.__enter__")
    def test_ensure_bucket_wraps_valueerror(self, mock_enter, mock_exit):
        mock_enter.side_effect = ValueError("bad bucket")

        with self.assertRaises(BucketCreatorError):
            self.creator.ensure_bucket("test-bucket")

    @patch("db.media.infrastructure.BucketCreator.BucketCreator.__enter__")
    @patch("db.media.infrastructure.BucketCreator.BucketCreator.__exit__")
    def test_ensure_bucket_wraps_generic_exception(self, mock_exit, mock_enter):
        mock_enter.side_effect = RuntimeError("other error")

        with self.assertRaises(BucketCreatorError):
            self.creator.ensure_bucket("test-bucket")


if __name__ == "__main__":
    unittest.main()
