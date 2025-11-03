import unittest
from unittest.mock import patch
from configs.reader.MinioBucketConfigReader import MinioBucketConfigReader
from configs.enum.ConfigEnum import MINIO_BUCKETS


class TestMinioBucketConfigReader(unittest.TestCase):

    def setUp(self):
        self.mock_config = {
            MINIO_BUCKETS.BUCKETS: {
                MINIO_BUCKETS.RAW_BUCKET: "raw-bucket",
                MINIO_BUCKETS.ANALYZED_BUCKET: "analyzed-bucket",
            }
        }

    @patch.object(MinioBucketConfigReader, "load_config")
    def test_get_bucket_methods(self, mock_load_config):
        mock_load_config.return_value = self.mock_config

        reader = MinioBucketConfigReader()

        buckets_data = reader._getBuckets()
        self.assertEqual(buckets_data, self.mock_config[MINIO_BUCKETS.BUCKETS])

        self.assertEqual(reader.getRawBucket(), "raw-bucket")
        self.assertEqual(reader.getAnalyzedBucket(), "analyzed-bucket")

    @patch.object(MinioBucketConfigReader, "load_config")
    def test_missing_buckets_section(self, mock_load_config):
        mock_load_config.return_value = {}
        reader = MinioBucketConfigReader()

        self.assertIsNone(reader.getRawBucket())
        self.assertIsNone(reader.getAnalyzedBucket())

    @patch.object(MinioBucketConfigReader, "load_config")
    def test_partial_bucket_config(self, mock_load_config):
        mock_load_config.return_value = {
            MINIO_BUCKETS.BUCKETS: {MINIO_BUCKETS.RAW_BUCKET: "raw-only"}
        }
        reader = MinioBucketConfigReader()

        self.assertEqual(reader.getRawBucket(), "raw-only")
        self.assertIsNone(reader.getAnalyzedBucket())

    @patch.object(MinioBucketConfigReader, "load_config")
    def test_bucket_edge_none_buckets_section(self, mock_load_config):
        mock_load_config.return_value = {MINIO_BUCKETS.BUCKETS: None}
        reader = MinioBucketConfigReader()
        self.assertIsNone(reader.getRawBucket())
        self.assertIsNone(reader.getAnalyzedBucket())

    @patch.object(MinioBucketConfigReader, "load_config")
    def test_bucket_edge_wrong_type_buckets_section(self, mock_load_config):
        mock_load_config.return_value = {MINIO_BUCKETS.BUCKETS: "not a dict"}
        reader = MinioBucketConfigReader()
        self.assertIsNone(reader.getRawBucket())
        self.assertIsNone(reader.getAnalyzedBucket())
