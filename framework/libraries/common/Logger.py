
# Logger.py
import logging

class Logger:
    def __init__(self, log_name='default_logger', log_file=None, level=logging.INFO):
        """
        Initialize the Logger instance.
        :param log_name: Name of the logger (default: 'default_logger')
        :param log_file: Optional log file path. If provided, logs will be written to the file.
        :param level: Logging level (default: logging.INFO)
        """
        # Create a logger instance
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(level)

        # Create a console handler (for output to the console)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # Create a formatter (for formatting the logs)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        # Add the console handler to the logger
        self.logger.addHandler(console_handler)

        # If log_file is provided, add a file handler to log to the specified file
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def info(self, message):
        """Log an info-level message."""
        self.logger.info(message)

    def debug(self, message):
        """Log a debug-level message."""
        self.logger.debug(message)

    def warning(self, message):
        """Log a warning-level message."""
        self.logger.warning(message)

    def error(self, message):
        """Log an error-level message."""
        self.logger.error(message)

    def critical(self, message):
        """Log a critical-level message."""
        self.logger.critical(message)
