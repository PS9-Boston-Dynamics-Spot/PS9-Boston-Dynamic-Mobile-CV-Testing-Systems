from common.exceptions.BaseAppException import BaseAppException


class MultipleIDsError(BaseAppException):

    def __init__(self, error_code: int, nodes: list, id: int):
        self.message = (
            f"Error: '{error_code}', OPCUA Nodes Config Reader has found multiple nodes for the ID '{id}', Nodes: '{nodes}'"
        )
        super().__init__(self.message)
