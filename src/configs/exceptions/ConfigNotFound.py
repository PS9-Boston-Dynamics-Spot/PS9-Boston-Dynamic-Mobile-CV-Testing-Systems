from common.exceptions.handler.LogHandler import LogHandler


class ConfigNotFound(BaseException):

    def __init__(self, exception: Exception, path: str, error_code: int):

        self.message = f"Error: '{error_code}', Config not found for path '{path}', Exception: '{exception}'"
        LogHandler.log_exception(self.message)

        super().__init__(self.message)
