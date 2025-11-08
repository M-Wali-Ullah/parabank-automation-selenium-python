"""
Custom logging configuration
"""
import sys
from loguru import logger
from config.config import Config

# Remove default logger
logger.remove()

# Configure file logging
Config.ensure_directories()
logger.add(
    Config.LOGS_DIR / "test_execution.log",
    rotation="10 MB",
    retention="30 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
)

# Configure console logging
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
)

def get_logger(name):
    """Get logger instance with specific name"""
    return logger.bind(name=name)