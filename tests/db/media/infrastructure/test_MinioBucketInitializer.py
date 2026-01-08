import unittest
from unittest.mock import patch

from db.media.infrastructure.MinioBucketInitializer import MinioBucketInitializer
from db.media.exceptions.BucketCreatorError import BucketCreatorError
from db.media.exceptions.BucketInitializerError import BucketInitializerError


class TestMinioBucketInitializer(unittest.TestCase):

    @patch("db.media.infrastructure.MinioBucketInitializer.BucketCreator")
    def test_initialize_bucket_success(self, mock_bucket_creator_cls):
        mock_creator = mock_bucket_creator_cls.return_value
        mock_creator.ensure_bucket.return_value = "my-bucket"

        initializer = MinioBucketInitializer(bucket_name="my-bucket")
        result = initializer.initalize_bucket()

        self.assertEqual(result, "my-bucket")
        mock_bucket_creator_cls.assert_called_once_with()
        mock_creator.ensure_bucket.assert_called_once_with("my-bucket")

    @patch("db.media.infrastructure.MinioBucketInitializer.BucketCreator")
    def test_initialize_bucket_wraps_bucketcreatorerror(self, mock_bucket_creator_cls):
        mock_creator = mock_bucket_creator_cls.return_value
        mock_creator.ensure_bucket.side_effect = BucketCreatorError(
            exception=ValueError("x"), error_code=123
        )

        initializer = MinioBucketInitializer("my-bucket")

        with self.assertRaises(BucketInitializerError):
            initializer.initalize_bucket()

    @patch("db.media.infrastructure.MinioBucketInitializer.BucketCreator")
    def test_initialize_bucket_wraps_generic_exception(self, mock_bucket_creator_cls):
        mock_creator = mock_bucket_creator_cls.return_value
        mock_creator.ensure_bucket.side_effect = RuntimeError("other")

        initializer = MinioBucketInitializer("my-bucket")

        with self.assertRaises(BucketInitializerError):
            initializer.initalize_bucket()


if __name__ == "__main__":
    unittest.main()
