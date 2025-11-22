from common.exceptions.BaseAppException import BaseAppException


class ReaderError(BaseAppException):
    def __init__(self, exception: Exception, node_id: str, error_code: int):
        self.exeption = exception
        self.node_id = node_id
        self.error_code = error_code
        self.message = f"Error: '{error_code}', Error during reading node: {node_id}, Exception: '{exception}'"
        super().__init__(self.message)
