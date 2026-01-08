import uuid


class ImageNames:
    @staticmethod
    def random() -> str:
        return str(uuid.uuid4())
