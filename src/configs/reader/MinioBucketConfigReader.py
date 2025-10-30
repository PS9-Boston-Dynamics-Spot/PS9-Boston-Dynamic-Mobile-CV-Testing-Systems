from typing import Dict, Any, Optional
from configs.loader.ConfigLoader import ConfigLoader
from configs.enum.ConfigEnum import ConfigEnum, MINIO_BUCKETS


class MinioBucketConfigReader(ConfigLoader):
    def __init__(self):
        super().__init__()
        self.__config = self.load_config(ConfigEnum.BUCKETS_CONFIG)

    def _getBuckets(self) -> Dict[str, Any]:
        return self.__config.get(MINIO_BUCKETS.BUCKETS, {})

    def getRawBucket(self) -> Optional[str]:
        return self._getBuckets().get(MINIO_BUCKETS.RAW_BUCKET)

    def getAnalyzedBucket(self) -> Optional[str]:
        return self._getBuckets().get(MINIO_BUCKETS.ANALYZED_BUCKET)
