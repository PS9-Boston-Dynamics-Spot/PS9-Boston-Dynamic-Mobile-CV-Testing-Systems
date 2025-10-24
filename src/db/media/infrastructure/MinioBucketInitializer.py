from db.media.infrastructure.BucketCreator import BucketCreator
from db.media.exceptions.BucketInitializerError import BucketInitializerError
from db.media.exceptions.BucketCreatorError import BucketCreatorError
from db.media.exceptions.BucketInitializerError import BucketInitializerError

class MinioBucketInitializer:
    def __init__(self, bucket_name: str = "ps9-analyzer-bucket"):
        self.bucket_name = bucket_name

    def initalize_bucket(self):
        try:
            bucket_name = BucketCreator().ensure_bucket(self.bucket_name)
            return bucket_name
        except BucketCreatorError as e:
            # TODO: Improve error handling, e.g. try again? 
            raise BucketInitializerError(exception=e, error_code=1761337280)
        except Exception as e:
            raise BucketInitializerError(exception=e, error_code=1761337290)