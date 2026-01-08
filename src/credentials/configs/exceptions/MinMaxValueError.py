from common.exceptions.BaseAppException import BaseAppException


class MinMaxValueError(BaseAppException):

    def __init__(self, error_code: int, id: int, min_value: float, max_value: float):
        self.error_code = error_code
        self.id = id
        self.min_value = min_value
        self.max_value = max_value
        self.message = f"Error: '{error_code}', OPCUA Nodes Config Reader has found node with ID '{id}' with invalid min value '{min_value}' and max value '{max_value}', The min value must be less than the max value"
        super().__init__(self.message)
