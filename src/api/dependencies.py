"""API dependencies for dependency injection."""

from functools import lru_cache
from ..agent.executor import FraudDetectionExecutor
from ..utils.logging import get_logger

logger = get_logger(__name__)


@lru_cache()
def get_fraud_executor() -> FraudDetectionExecutor:
    """Get fraud detection executor instance (singleton)."""
    logger.info("Creating FraudDetectionExecutor instance")
    return FraudDetectionExecutor()
