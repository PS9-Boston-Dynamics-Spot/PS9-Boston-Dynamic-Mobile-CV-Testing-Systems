import logging
import os
from typing import Optional

class LogHandler:
    _initialized = False
    _logger = None
    
    @classmethod
    def initialize(cls, log_file: str = "app.log", level=logging.INFO, 
                   log_format: str = None, date_format: str = None):
        """Initialisiert den Logger einmalig"""
        if cls._initialized:
            return
            
        if log_format is None:
            log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        if date_format is None:
            date_format = "%Y-%m-%d %H:%M:%S"
            
        cls._logger = logging.getLogger("AppLogger")
        cls._logger.setLevel(level)
        
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        cls._logger.addHandler(file_handler)
        cls._logger.addHandler(console_handler)
        
        cls._initialized = True
    
    @classmethod
    def _ensure_initialized(cls):
        if not cls._initialized:
            cls.initialize()
    
    @classmethod
    def log_info(cls, message: str) -> None:
        cls._ensure_initialized()
        cls._logger.info(message)
    
    @classmethod
    def log_debug(cls, message: str) -> None:
        cls._ensure_initialized()
        cls._logger.debug(message)
    
    @classmethod
    def log_warning(cls, message: str) -> None:
        cls._ensure_initialized()
        cls._logger.warning(message)
    
    @classmethod
    def log_error(cls, message: str) -> None:
        cls._ensure_initialized()
        cls._logger.error(message)
    
    @classmethod
    def log_exception(cls, message: str, exc: Optional[Exception] = None) -> None:
        cls._ensure_initialized()
        if exc:
            cls._logger.error(f"{message}: {str(exc)}", exc_info=exc)
        else:
            cls._logger.exception(message)