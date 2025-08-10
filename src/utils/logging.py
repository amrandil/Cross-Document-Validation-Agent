"""Logging configuration for the fraud detection agent."""

import sys
from typing import Optional
from loguru import logger

from ..config import settings


def setup_logging() -> None:
    """Configure logging for the application."""
    # Remove default handler
    logger.remove()

    # Add handler based on configuration
    if settings.log_format.lower() == "json":
        logger.add(
            sys.stderr,
            format="{{\"timestamp\": \"{time:YYYY-MM-DD HH:mm:ss.SSS}\", \"level\": \"{level}\", \"message\": \"{message}\", \"module\": \"{name}\", \"function\": \"{function}\", \"line\": {line}}}",
            level=settings.log_level,
            colorize=False,
            serialize=True
        )
    else:
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.log_level,
            colorize=True
        )

    # Add file handler for production
    if settings.environment.lower() == "production":
        logger.add(
            "logs/fraud_detection.log",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            level=settings.log_level,
            rotation="10 MB",
            retention="30 days",
            compression="gz"
        )


def get_logger(name: Optional[str] = None):
    """Get a logger instance."""
    if name:
        return logger.bind(name=name)
    return logger


# Initialize logging on import
setup_logging()
