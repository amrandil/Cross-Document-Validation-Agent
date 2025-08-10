"""API models for the fraud detection service."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from .documents import Document, DocumentBundle
from .fraud import AgentExecution, FraudAnalysisResult


class AnalysisRequest(BaseModel):
    """Request model for document analysis."""
    bundle_id: Optional[str] = Field(
        None, description="Optional bundle ID, will be generated if not provided")
    documents: List[Dict[str, Any]
                    ] = Field(..., description="List of document data")
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Analysis options")

    class Config:
        json_schema_extra = {
            "example": {
                "bundle_id": "bundle_123",
                "documents": [
                    {
                        "document_type": "commercial_invoice",
                        "filename": "invoice.pdf",
                        "content": "Invoice content here..."
                    },
                    {
                        "document_type": "packing_list",
                        "filename": "packing.pdf",
                        "content": "Packing list content here..."
                    }
                ],
                "options": {
                    "confidence_threshold": 0.7,
                    "detailed_analysis": True
                }
            }
        }


class AnalysisResponse(BaseModel):
    """Response model for document analysis."""
    success: bool
    bundle_id: str
    execution_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Agent execution details
    agent_execution: AgentExecution

    # Analysis results
    fraud_analysis: Optional[FraudAnalysisResult] = None

    # Metadata
    processing_time_ms: int
    documents_processed: int
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
    uptime_seconds: float
    environment: str
    dependencies: Dict[str, str] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response model."""
    error: bool = True
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": True,
                "message": "Invalid document type provided",
                "error_code": "INVALID_DOCUMENT_TYPE",
                "details": {
                    "provided_type": "unknown_document",
                    "supported_types": ["commercial_invoice", "packing_list", "bill_of_lading"]
                },
                "timestamp": "2024-01-01T12:00:00Z",
                "request_id": "req_123"
            }
        }


class DocumentUpload(BaseModel):
    """Model for document upload via form data."""
    document_type: str
    filename: str
    content: bytes

    def to_document(self) -> Document:
        """Convert to Document model."""
        return Document(
            document_type=self.document_type,
            filename=self.filename,
            content=self.content.decode(
                'utf-8') if isinstance(self.content, bytes) else self.content
        )
