from common.exceptions.handler.LogHandler import LogHandler


class ConfigLoadError(BaseException):

    def __init__(self, exception: Exception, error_code: int):
        self.message = (
            f"Error: '{error_code}', Config could not loaded, Exception: '{exception}'"
        )
        LogHandler.log_exception(self.message)

        super().__init__(self.message)
