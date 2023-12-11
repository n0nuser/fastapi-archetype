import logging
import os
import shutil
import tempfile
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create a logger object
logger = logging.getLogger(__name__)

# Set the logger level
logger.setLevel(logging.INFO)

# Create a formatter object
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Determine log file path
log_file_path_env = os.getenv("APP_LOG_FILE_PATH", "logs/app.log")
log_file_path = Path(log_file_path_env).resolve()
if not log_file_path.parent.exists():
    log_file_path.parent.mkdir(parents=True)
if not log_file_path.exists():
    log_file_path.touch()

# Calculate the maximum log file size (15% of disk capacity or 4GB, whichever is smaller)
max_log_size = min(
    0.15 * shutil.disk_usage(log_file_path.parent).total, 4 * 1024 * 1024 * 1024
)

# Create a temporary directory to hold old log files
temp_dir = Path(tempfile.mkdtemp())

# Create a RotatingFileHandler with log rotation based on size
file_handler = RotatingFileHandler(
    log_file_path, maxBytes=int(max_log_size), backupCount=10
)

# Set the formatter for the file handler
file_handler.setFormatter(formatter)

# Add the file handler to the logger object
logger.addHandler(file_handler)

# Create a stream handler
stream_handler = logging.StreamHandler()

# Set the formatter for the stream handler
stream_handler.setFormatter(formatter)

# Add the stream handler to the logger object
logger.addHandler(stream_handler)


# Clean up old log files in the temporary directory
threshold = datetime.now() - timedelta(days=7)  # Remove log files older than 7 days

for old_log_file in temp_dir.glob("*.log"):
    try:
        file_time = datetime.fromtimestamp(old_log_file.stat().st_mtime)
        if file_time < threshold:
            old_log_file.unlink()
    except Exception as error:
        logger.error(f"Failed to delete old log file {old_log_file}: {error}")

# Remove the temporary directory
try:
    temp_dir.rmdir()
except Exception as error:
    logger.error(f"Failed to remove temporary directory {temp_dir}: {error}")
