import ssl
import unittest
from unittest.mock import patch, MagicMock

from db.media.connector.MinioConnector import MinioConnector
from db.media.exceptions.MinioInitError import MinioInitError
from db.media.exceptions.MinioConnectionError import MinioConnectionError


class TestMinioConnectorInit(unittest.TestCase):

    @patch("db.media.connector.MinioConnector.MinioConfigReader")
    def test_init_success_sets_attributes_and_endpoint(self, mock_reader_cls):
        mock_reader = mock_reader_cls.return_value
        mock_reader.getHost.return_value = "localhost"
        mock_reader.getPort.return_value = "9000"
        mock_reader.getAccessKey.return_value = "access"
        mock_reader.getSecretKey.return_value = "secret"
        mock_reader.getTls.return_value = True

        connector = MinioConnector()

        self.assertEqual(connector.host, "localhost")
        self.assertEqual(connector.port, "9000")
        self.assertEqual(connector.access_key, "access")
        self.assertEqual(connector.secret_key, "secret")
        self.assertTrue(connector.tls)
        self.assertEqual(connector.endpoint, "localhost:9000")

    @patch("db.media.connector.MinioConnector.MinioConfigReader")
    def test_init_sets_tls_false_if_not_truthy(self, mock_reader_cls):
        mock_reader = mock_reader_cls.return_value
        mock_reader.getHost.return_value = "localhost"
        mock_reader.getPort.return_value = "9000"
        mock_reader.getAccessKey.return_value = "access"
        mock_reader.getSecretKey.return_value = "secret"
        mock_reader.getTls.return_value = None

        connector = MinioConnector()
        self.assertFalse(connector.tls)

    @patch("db.media.connector.MinioConnector.MinioConfigReader")
    def test_init_raises_minioiniterror_if_config_missing(self, mock_reader_cls):
        mock_reader = mock_reader_cls.return_value
        mock_reader.getHost.return_value = None
        mock_reader.getPort.return_value = "9000"
        mock_reader.getAccessKey.return_value = "access"
        mock_reader.getSecretKey.return_value = "secret"
        mock_reader.getTls.return_value = False

        with self.assertRaises(MinioInitError):
            MinioConnector()


class TestMinioConnectorConnect(unittest.TestCase):

    def setUp(self):
        patcher = patch("db.media.connector.MinioConnector.MinioConfigReader")
        self.addCleanup(patcher.stop)
        mock_reader_cls = patcher.start()
        mock_reader = mock_reader_cls.return_value
        mock_reader.getHost.return_value = "localhost"
        mock_reader.getPort.return_value = "9000"
        mock_reader.getAccessKey.return_value = "access"
        mock_reader.getSecretKey.return_value = "secret"
        mock_reader.getTls.return_value = False

        self.connector = MinioConnector()

    @patch("db.media.connector.MinioConnector.Minio")
    def test_connect_success_creates_client(self, mock_minio_cls):
        mock_client = MagicMock()
        mock_minio_cls.return_value = mock_client

        self.connector._connect()

        mock_minio_cls.assert_called_once_with(
            endpoint="localhost:9000",
            access_key="access",
            secret_key="secret",
            secure=False,
        )
        self.assertIs(self.connector.client, mock_client)

    @patch("db.media.connector.MinioConnector.Minio")
    def test_connect_raises_minio_connection_error_on_connectionerror(
        self, mock_minio_cls
    ):
        mock_minio_cls.side_effect = ConnectionError("cannot connect")

        with self.assertRaises(MinioConnectionError):
            self.connector._connect()

    @patch("db.media.connector.MinioConnector.Minio")
    def test_connect_raises_minio_connection_error_on_ssl_error(self, mock_minio_cls):
        mock_minio_cls.side_effect = ssl.SSLError("ssl error")

        with self.assertRaises(MinioConnectionError):
            self.connector._connect()

    @patch("db.media.connector.MinioConnector.Minio")
    def test_connect_raises_minio_connection_error_on_generic_exception(
        self, mock_minio_cls
    ):
        mock_minio_cls.side_effect = RuntimeError("some error")

        with self.assertRaises(MinioConnectionError):
            self.connector._connect()


class TestMinioConnectorContextManager(unittest.TestCase):

    @patch("db.media.connector.MinioConnector.Minio")
    @patch("db.media.connector.MinioConnector.MinioConfigReader")
    def test_context_manager_enters_and_exits(self, mock_reader_cls, mock_minio_cls):
        mock_reader = mock_reader_cls.return_value
        mock_reader.getHost.return_value = "localhost"
        mock_reader.getPort.return_value = "9000"
        mock_reader.getAccessKey.return_value = "access"
        mock_reader.getSecretKey.return_value = "secret"
        mock_reader.getTls.return_value = False

        mock_client = MagicMock()
        mock_minio_cls.return_value = mock_client

        connector = MinioConnector()

        with connector as client:
            self.assertIs(client, mock_client)
            self.assertIs(connector.client, mock_client)

        self.assertIsNone(connector.client)


if __name__ == "__main__":
    unittest.main()
