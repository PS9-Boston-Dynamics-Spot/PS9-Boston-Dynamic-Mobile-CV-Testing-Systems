from common.exceptions.BaseAppException import BaseAppException


class NodeDoesNotExistError(BaseAppException):

    def __init__(self, error_code: int, aruco_id: list):
        self.error_code = error_code
        self.aruco_id = aruco_id
        self.message = f"Error: '{error_code}', OPCUA Nodes Config Reader has not found nodes for the ID '{aruco_id}'"
        super().__init__(self.message)
