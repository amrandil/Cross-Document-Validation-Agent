"""API package for the fraud detection service."""

from .routes import router
from .dependencies import get_fraud_executor

__all__ = ["router", "get_fraud_executor"]
