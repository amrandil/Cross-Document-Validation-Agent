"""Pydantic models for the fraud detection agent."""

from .documents import (
    Document,
    DocumentType,
    CommercialInvoice,
    PackingList,
    BillOfLading,
    CertificateOfOrigin,
    CustomsDeclaration,
    DocumentBundle
)

from .fraud import (
    FraudType,
    FraudIndicator,
    FraudEvidence,
    FraudAnalysisResult,
    AgentStep,
    AgentExecution
)

from .api import (
    AnalysisRequest,
    AnalysisResponse,
    HealthResponse,
    ErrorResponse
)

__all__ = [
    # Documents
    "Document",
    "DocumentType",
    "CommercialInvoice",
    "PackingList",
    "BillOfLading",
    "CertificateOfOrigin",
    "CustomsDeclaration",
    "DocumentBundle",
    # Fraud
    "FraudType",
    "FraudIndicator",
    "FraudEvidence",
    "FraudAnalysisResult",
    "AgentStep",
    "AgentExecution",
    # API
    "AnalysisRequest",
    "AnalysisResponse",
    "HealthResponse",
    "ErrorResponse"
]
