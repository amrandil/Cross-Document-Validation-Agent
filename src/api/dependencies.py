"""API dependencies for dependency injection."""

from functools import lru_cache
from ..agent.executor import FraudDetectionExecutor


@lru_cache()
def get_fraud_executor() -> FraudDetectionExecutor:
    """Get fraud detection executor instance (singleton)."""
    return FraudDetectionExecutor()
