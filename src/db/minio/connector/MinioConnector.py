from minio import Minio
from configs.reader.MinioConfigReader import MinioConfigReader
from minio.error import S3Error
from db.minio.exceptions.MinioConnectionError import MinioConnectionError
from db.minio.exceptions.MinioInitError import MinioInitError

class MinioConnector:

    def __init__(self):
        self.minio_config_reader = MinioConfigReader()
        self.host = self.minio_config_reader.getHost()
        self.port = self.minio_config_reader.getPort()
        self.access_key = self.minio_config_reader.getAccessKey()
        self.secret_key = self.minio_config_reader.getSecretKey()
        self.tls = self.minio_config_reader.getTls()

        if not self.tls:
            self.tls = False

        if not all([self.host, self.port, self.access_key, self.secret_key]):
            raise MinioInitError(
                exception=ValueError("Error in MinIO configuration: Host, Port, AccessKey or SecretKey is missing"),
                error_code=1761165390,
                host=self.host,
                port=self.port,
                access_key=self.access_key,
                secret_key=self.secret_key
            )
            
        self.endpoint = f"{self.host}:{self.port}"

    def _connect(self):
        try:
            self.client = Minio(
                endpoint=self.endpoint, 
                access_key=self.access_key, 
                secret_key=self.secret_key, 
                secure=self.tls
            )
        except (S3Error, ConnectionError) as e:
            raise MinioConnectionError(e, 1761164520)
        except Exception as e:
            raise MinioConnectionError(e, 1761164530)

    def __enter__(self):
        self._connect()
        return self.client
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass
