
from minio import Minio
from configs.unified_config_manager import UnifiedConfigManager


class MinioConnector:
    def __init__(self, config_manager: UnifiedConfigManager | None = None) -> None:
        self._config_manager = config_manager or UnifiedConfigManager()
        self._client: Minio | None = None

    def connect(self) -> Minio:
        cfg = self._config_manager.getMinioCreds()

        endpoint = f"{cfg['host']}:{cfg['port']}"
        self._client = Minio(
            endpoint=endpoint,
            access_key=cfg["access_key"],
            secret_key=cfg["secret_key"],
            secure=bool(cfg["tls"]),
        )
        return self._client
