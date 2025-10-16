from src.common.exceptions.LogHandler import LogHandler

class ConfigNotFound(Exception):
    @staticmethod
    def log_error(message: str) -> None:
        LogHandler.log_error(f"ConfigNotFound: {message}")
    
    @staticmethod
    def log_warning(message: str) -> None:
        LogHandler.log_exception(f"ConfigNotFound: {message}")


class ConfigParseError(Exception):
    @staticmethod
    def log_error(message: str) -> None:
        LogHandler.log_error(f"ConfigParseError: {message}")
    
    @staticmethod
    def log_exception(message: str) -> None:
        LogHandler.log_exception(f"ConfigParseError: {message}")