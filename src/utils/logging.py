"""Logging configuration for the fraud detection agent."""

import sys
import os
from typing import Optional
from loguru import logger

from ..config import settings


def setup_logging() -> None:
    """Configure logging for the application."""
    # Ensure log directory exists (use /log as requested)
    log_dir = os.path.join(os.getcwd(), "log")
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception:
        # Fallback to local directory if creation fails
        log_dir = "log"
        os.makedirs(log_dir, exist_ok=True)

    # Remove default handler
    logger.remove()

    # Console handler
    if settings.log_format.lower() == "json":
        logger.add(
            sys.stderr,
            format="{{\"timestamp\": \"{time:YYYY-MM-DD HH:mm:ss.SSS}\", \"level\": \"{level}\", \"message\": \"{message}\", \"module\": \"{name}\", \"function\": \"{function}\", \"line\": {line}}}",
            level=settings.log_level,
            colorize=False,
            serialize=True,
        )
    else:
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.log_level,
            colorize=True,
        )

    # File handler (always enabled)
    logger.add(
        os.path.join(log_dir, "app.log"),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="10 MB",
        retention="30 days",
        compression="gz",
        enqueue=True,
        backtrace=True,
        diagnose=False,
    )


def get_logger(name: Optional[str] = None):
    """Get a logger instance."""
    if name:
        return logger.bind(name=name)
    return logger


# Initialize logging on import
setup_logging()
