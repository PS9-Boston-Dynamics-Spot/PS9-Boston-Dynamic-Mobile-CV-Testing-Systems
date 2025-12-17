from common.exceptions.BaseAppException import BaseAppException


class CategoryDoesNotExistError(BaseAppException):

    def __init__(self, error_code: int, category_name: str, aruco_id: int):
        self.error_code = error_code
        self.aruco_id = aruco_id
        self.category_name = category_name
        self.message = f"Error: '{error_code}', Sensors Config Reader has not found category '{category_name}' for the ID '{aruco_id}'"
        super().__init__(self.message)
