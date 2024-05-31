"""Module to keep track of loggings in the app."""

import logging
import os
import shutil
from datetime import datetime, timedelta, timezone
from enum import Enum
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal

from asgi_correlation_id import CorrelationIdFilter

from src.core.config import settings


class LogLevelColor(Enum):
    """Mapping of log levels to ANSI escape codes for colored output."""

    DEBUG = "\033[94m"  # Blue
    INFO = "\033[92m"  # Green
    WARNING = "\033[93m"  # Yellow
    ERROR = "\033[91m"  # Red
    CRITICAL = "\033[91m\033[1m"  # Red + Bold


class ColoredConsoleFormatter(logging.Formatter):
    """A logging formatter that adds color to console log messages based on the level of severity.

    This formatter allows for both colorization of the log header and formatting of the
    message content, making it easier to distinguish logs based on their importance at
    a glance.

    Attributes:
        default_fmt (logging.Formatter): Formatter for the message part of the
            log without any color.
        header_fmt (logging.Formatter): Formatter for the header part of the log,
            including timestamps, logger name, function name, and log level.

    Args:
        fmt (str, optional): The log format string to use. Defaults to None.
        datefmt (str, optional): The date format string to use. Defaults to None.
        style (str, optional): The style specifier for formatting. Defaults to '%'.
    """

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
    ):
        """Initializes the formatter with optional format, date format, and style.

        The constructor sets up the formatters for the message and header with or without custom
        formatting specifications.

        Args:
            fmt (str, optional): The log format string to use. Defaults to None.
            datefmt (str, optional): The date format string to use. Defaults to None.
            style (str, optional): The style specifier for formatting. Defaults to '%'.
        """
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        # Define the basic uncolored format for the message part
        self.default_fmt = logging.Formatter("%(message)s", datefmt=datefmt)
        self.header_fmt = logging.Formatter(
            "%(asctime)s - [%(correlation_id)s] - %(name)s - %(funcName)s - %(levelname)s",
            datefmt=datefmt,
        )

    def format(self, record: logging.LogRecord) -> str:
        """Formats the log record into a color-coded string.

        This method applies color to the log header based on the log level, and combines it with the
        uncolored message part of the log record.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log record with a color-coded header.
        """
        header = self.header_fmt.format(record)
        message = self.default_fmt.format(record)
        if record.levelname in LogLevelColor.__members__:
            color = LogLevelColor[record.levelname].value
            header = f"{color}{header}\033[0m"  # Apply color to header and reset to default after
        return f"{header} - {message}"  # Combine colored header with default message


def setup_logging() -> None:
    """Configure the root logger for the application."""
    cid_filter = CorrelationIdFilter(uuid_length=32)
    log_format = (
        "%(asctime)s - [%(correlation_id)s] - %(name)s - %(funcName)s - %(levelname)s - %(message)s"
    )
    level = logging.DEBUG if settings.ENVIRONMENT in ["DEV", "PYTEST"] else logging.INFO

    # Create a formatter object
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
    file_handler.addFilter(cid_filter)

    # Setup console handler with color
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(cid_filter)

    # Clear existing handlers
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Add Handlers
    root_logger.setLevel(level)
    logging.getLogger().addHandler(console_handler)
    logging.getLogger().addHandler(file_handler)

    # Suppress specific library logs
    library_logger = logging.getLogger("pytds")
    library_logger.setLevel(logging.ERROR)  # Set to ERROR to suppress DEBUG and INFO logs


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


if __name__ == "__main__":
    setup_logging()
    logging.debug("This is a debug message.")
    logging.info("This is an info message.")
    logging.warning("This is a warning message.")
    logging.error("This is an error message.")
    logging.critical("This is a critical message.")
    log_dir = Path("logs")  # Assuming logs are stored here
    cleanup_old_logs(log_dir, retention_days=7)
