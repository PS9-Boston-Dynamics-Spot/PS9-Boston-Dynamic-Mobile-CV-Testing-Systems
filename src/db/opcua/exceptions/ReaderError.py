from common.exceptions.BaseAppException import BaseAppException


class ReaderError(BaseAppException):
    def __init__(self, exception: Exception, node_id: str, error_code: int):
        self.message = f"Error: '{error_code}', Error during reading node: {node_id}, Exception: '{exception}'"
        super().__init__(self.message)
