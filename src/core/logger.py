"""Module to keep track of loggings in the app."""

import logging
import os
import shutil
from datetime import datetime, timedelta, timezone
from enum import Enum
from logging.handlers import RotatingFileHandler
from pathlib import Path


class LogLevelColor(Enum):
    """Mapping of log levels to ANSI escape codes for colored output."""

    DEBUG = "\033[94m"  # Blue
    INFO = "\033[92m"  # Green
    WARNING = "\033[93m"  # Yellow
    ERROR = "\033[91m"  # Red
    CRITICAL = "\033[91m\033[1m"  # Red + Bold


class ColoredConsoleFormatter(logging.Formatter):
    """A logging formatter that adds color to console log messages based on level."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the console log message with color based on the level."""
        log_message = super().format(record)
        if record.levelname in LogLevelColor.__members__:
            color = LogLevelColor[record.levelname].value
            log_message = f"{color}{log_message}\033[0m"  # Reset to default color at the end
        return log_message


def setup_logging() -> logging.Logger:
    """Configure logging for the application."""
    # Create a logger object
    logger = logging.getLogger(__name__)

    # Set the logger level
    logger.setLevel(logging.DEBUG)

    # Create a formatter object
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_formatter = logging.Formatter(log_format)
    console_formatter = ColoredConsoleFormatter(log_format)

    # Determine log file path
    log_file_path_env = os.getenv("APP_LOG_FILE_PATH", "logs/app.log")
    log_file_path = Path(log_file_path_env).resolve()

    if not log_file_path.parent.exists():
        log_file_path.parent.mkdir(parents=True)
    if not log_file_path.exists():
        log_file_path.touch()

    # Calculate the maximum log file size (15% of disk capacity or 4GB, whichever is smaller)
    max_log_size = min(
        0.15 * shutil.disk_usage(log_file_path.parent).total,
        4 * 1024 * 1024 * 1024,
    )

    # Create a RotatingFileHandler with log rotation based on size
    file_handler = RotatingFileHandler(
        str(log_file_path),
        maxBytes=int(max_log_size),
        backupCount=10,
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Setup console handler with color
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    logging.info("Logging setup complete.")

    return logger


def cleanup_old_logs(log_directory: Path, retention_days: int = 7) -> None:
    """Remove log files older than a specified number of days.

    Args:
        log_directory: The directory containing log files to clean up.
        retention_days: The number of days to retain log files.
            Files older than this will be deleted.
    """
    threshold = datetime.now(timezone.utc) - timedelta(days=retention_days)

    log_file = ""
    error = ""
    try:
        for log_file in log_directory.glob("*.log"):
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime, tz=timezone.utc)
            if file_time < threshold:
                log_file.unlink()
                logging.info("Deleted old log file: %s", log_file)
    except OSError as error:
        logging.exception("Failed to delete old log file %s: %s", log_file, error)  # noqa: TRY401


# Optionally, for cleaning temporary directory specifically created for logs:
def cleanup_temp_log_dir(temp_dir: Path) -> None:
    """Remove a temporary directory used for holding log files, ensuring it's empty."""
    try:
        temp_dir.rmdir()  # Only succeeds if directory is empty
        logging.info("Removed temporary log directory: %s", temp_dir)
    except OSError as error:
        logging.exception(
            "Failed to remove temporary directory %s: %s",
            temp_dir,
            error,  # noqa: TRY401
        )


logger = setup_logging()

if __name__ == "__main__":
    setup_logging()
    logging.debug("This is a debug message.")
    logging.info("This is an info message.")
    logging.warning("This is a warning message.")
    logging.error("This is an error message.")
    logging.critical("This is a critical message.")
    log_dir = Path("logs")  # Assuming logs are stored here
    cleanup_old_logs(log_dir, retention_days=7)
