import logging


class Handler:
    """
    Basisklasse für alle Child-Klassen.
    Zuständig für zentrales Logging und Exception Handling.
    """

    def __init__(self, log_file: str = "app.log", level=logging.INFO):
        """
        Initialisiert das Logging.
        :param log_file: Pfad zur Logdatei
        :param level: Logging-Level (z.B. INFO, DEBUG, ERROR)
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(level)

        # Verhindert doppelte Handler bei mehrfacher Initialisierung
        if not self.logger.handlers:

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)

            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def log_info(self, message: str) -> None:
        self.logger.info(message)

    def log_debug(self, message: str) -> None:
        self.logger.debug(message)

    def log_warning(self, message: str) -> None:
        self.logger.warning(message)

    def log_error(self, message: str) -> None:
        self.logger.error(message)

    def log_exception(self, exception: Exception, context: str = "") -> None:
        self.logger.exception(f"{context}: {str(exception)}")
