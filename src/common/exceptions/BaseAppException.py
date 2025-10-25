from common.exceptions.handler.LogHandler import LogHandler


class BaseAppException(BaseException):
    def __init__(self, message: str):
        LogHandler.log_exception(message)
        super().__init__(message)
