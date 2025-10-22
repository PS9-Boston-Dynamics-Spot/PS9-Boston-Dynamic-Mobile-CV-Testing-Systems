from common.exceptions.handler.LogHandler import LogHandler


class ConfigParseError(BaseException):

    def __init__(self, exception: Exception, error_code: int):
        self.message = (
            f"Error: '{error_code}', Config could not parsed, Exception: '{exception}'"
        )
        LogHandler.log_error(self.message)

        super().__init__(self.message)
