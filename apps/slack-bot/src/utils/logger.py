import logging
import sys
import os
from typing import Any
from pathlib import Path

class RevolvLogger:
    """Enhanced logger for Revolvr AI Bot with dynamic configuration and structured logging."""
    
    def __init__(self, name: str = "revolver_ai_bot", level: int = logging.INFO):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        self._setup_console_handler()
        self._file_handler = None
    
    def _setup_console_handler(self) -> None:
        """Setup console handler with default formatting."""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(self._logger.level)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        
        # Avoid adding multiple handlers
        if not self._logger.handlers:
            self._logger.addHandler(handler)
    
    def set_level(self, level: int) -> None:
        """Dynamically change the logging level.
        
        Args:
            level: The new logging level (e.g., logging.DEBUG, logging.INFO)
        """
        self._logger.setLevel(level)
        for handler in self._logger.handlers:
            handler.setLevel(level)
    
    def add_file_handler(self, log_file: str) -> None:
        """Add a file handler to also log messages to a file.
        
        Args:
            log_file: Path to the log file
        """
        if self._file_handler:
            self._logger.removeHandler(self._file_handler)
        
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            
        self._file_handler = logging.FileHandler(log_file)
        self._file_handler.setLevel(self._logger.level)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        self._file_handler.setFormatter(formatter)
        self._logger.addHandler(self._file_handler)
    
    def remove_file_handler(self) -> None:
        """Remove the current file handler if it exists."""
        if self._file_handler:
            self._logger.removeHandler(self._file_handler)
            self._file_handler = None
    
    def structured(self, level: int, message: str, **kwargs: Any) -> None:
        """Log a structured message with additional context.
        
        Args:
            level: Logging level
            message: Main log message
            **kwargs: Additional key-value pairs to include in the log
        """
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        self._logger.log(level, message)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message, optionally with structured context."""
        self.structured(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message, optionally with structured context."""
        self.structured(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message, optionally with structured context."""
        self.structured(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message, optionally with structured context."""
        self.structured(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs: Any) -> None:
        """Log a critical message, optionally with structured context."""
        self.structured(logging.CRITICAL, message, **kwargs)

# Create singleton instance
logger = RevolvLogger()

# Export the logger instance for backward compatibility
logger_instance = logger._logger
