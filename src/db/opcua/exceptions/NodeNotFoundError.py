from common.exceptions.BaseAppException import BaseAppException


class NodeNotFoundError(BaseAppException):
    def __init__(self, exception: Exception, node_id: str, error_code: int):
        self.message = f"Error: '{error_code}', No node found with id: {node_id}, Exception: '{exception}'"
        super().__init__(self.message)
