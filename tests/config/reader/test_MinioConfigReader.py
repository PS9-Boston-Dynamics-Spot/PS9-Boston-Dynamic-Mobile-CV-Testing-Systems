import unittest
from unittest.mock import patch
from configs.reader.MinioConfigReader import MinioConfigReader
from configs.enum.ConfigEnum import MINIO_KEYS


class TestMinioConfigReader(unittest.TestCase):

    def setUp(self):
        self.mock_config = {
            MINIO_KEYS.MINIO: {
                MINIO_KEYS.HOST: "localhost",
                MINIO_KEYS.PORT: "9000",
                MINIO_KEYS.ACCESS_KEY: "minioadmin",
                MINIO_KEYS.SECRET_KEY: "miniosecret",
                MINIO_KEYS.TLS: True,
            }
        }

    @patch.object(MinioConfigReader, "load_config")
    def test_get_minio_methods(self, mock_load_config):
        mock_load_config.return_value = self.mock_config

        reader = MinioConfigReader()

        minio_data = reader._getMinio()
        self.assertEqual(minio_data, self.mock_config[MINIO_KEYS.MINIO])

        self.assertEqual(reader.getHost(), "localhost")
        self.assertEqual(reader.getPort(), "9000")
        self.assertEqual(reader.getAccessKey(), "minioadmin")
        self.assertEqual(reader.getSecretKey(), "miniosecret")
        self.assertTrue(reader.getTls())

    @patch.object(MinioConfigReader, "load_config")
    def test_missing_minio_section(self, mock_load_config):
        mock_load_config.return_value = {}
        reader = MinioConfigReader()

        self.assertIsNone(reader.getHost())
        self.assertIsNone(reader.getPort())
        self.assertIsNone(reader.getAccessKey())
        self.assertIsNone(reader.getSecretKey())
        self.assertIsNone(reader.getTls())

    @patch.object(MinioConfigReader, "load_config")
    def test_partial_minio_config(self, mock_load_config):
        mock_load_config.return_value = {
            MINIO_KEYS.MINIO: {MINIO_KEYS.HOST: "minio", MINIO_KEYS.PORT: "9001"}
        }
        reader = MinioConfigReader()

        self.assertEqual(reader.getHost(), "minio")
        self.assertEqual(reader.getPort(), "9001")
        self.assertIsNone(reader.getAccessKey())
        self.assertIsNone(reader.getSecretKey())
        self.assertIsNone(reader.getTls())

    @patch.object(MinioConfigReader, "load_config")
    def test_minio_edge_none_minio_section(self, mock_load_config):
        mock_load_config.return_value = {MINIO_KEYS.MINIO: None}
        reader = MinioConfigReader()
        self.assertIsNone(reader.getHost())
        self.assertIsNone(reader.getPort())
        self.assertIsNone(reader.getAccessKey())
        self.assertIsNone(reader.getSecretKey())
        self.assertIsNone(reader.getTls())

    @patch.object(MinioConfigReader, "load_config")
    def test_minio_edge_wrong_type_minio_section(self, mock_load_config):
        mock_load_config.return_value = {MINIO_KEYS.MINIO: 12345}
        reader = MinioConfigReader()
        self.assertIsNone(reader.getHost())
        self.assertIsNone(reader.getPort())
        self.assertIsNone(reader.getAccessKey())
        self.assertIsNone(reader.getSecretKey())
        self.assertIsNone(reader.getTls())
