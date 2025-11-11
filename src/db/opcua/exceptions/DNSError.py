from common.exceptions.BaseAppException import BaseAppException


class DNSError(BaseAppException):
    def __init__(self, exception: Exception, error_code: int):
        self.message = f"Error: '{error_code}', DNS-Auflösung fehlgeschlagen, Exception: '{exception}'"
        super().__init__(self.message)
