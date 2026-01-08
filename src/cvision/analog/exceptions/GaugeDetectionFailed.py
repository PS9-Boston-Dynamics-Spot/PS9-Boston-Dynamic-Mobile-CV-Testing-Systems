from common.exceptions.BaseAppException import BaseAppException


class GaugeDetectionFailed(BaseAppException):
    def __init__(self, error_code: int):
        self.error_code = error_code
        self.message = f"Error: '{error_code}', Gauge detection failed"
        super().__init__(self.message)
