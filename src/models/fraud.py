"""Fraud detection models."""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class FraudType(str, Enum):
    """Types of fraud that can be detected."""
    VALUATION_FRAUD = "valuation_fraud"
    QUANTITY_MANIPULATION = "quantity_manipulation"
    WEIGHT_MANIPULATION = "weight_manipulation"
    ORIGIN_MANIPULATION = "origin_manipulation"
    PRODUCT_SUBSTITUTION = "product_substitution"
    ENTITY_MISREPRESENTATION = "entity_misrepresentation"
    DOCUMENT_FORGERY = "document_forgery"


class FraudIndicator(BaseModel):
    """Individual fraud indicator found during analysis."""
    indicator_type: FraudType
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0,
                              description="Confidence score between 0 and 1")
    severity: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    evidence: List[str] = Field(
        default_factory=list, description="Supporting evidence")
    affected_documents: List[str] = Field(
        default_factory=list, description="Documents involved")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Additional details")


class FraudEvidence(BaseModel):
    """Evidence supporting fraud detection."""
    source_document: str
    field_name: str
    expected_value: Optional[str] = None
    actual_value: str
    discrepancy_type: str
    impact_assessment: str


class FraudAnalysisResult(BaseModel):
    """Complete fraud analysis result."""
    bundle_id: str
    analysis_id: str = Field(...,
                             description="Unique identifier for this analysis")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Overall Assessment
    fraud_detected: bool
    overall_confidence: float = Field(..., ge=0.0, le=1.0)
    risk_level: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")

    # Detailed Findings
    fraud_indicators: List[FraudIndicator] = Field(default_factory=list)
    evidence: List[FraudEvidence] = Field(default_factory=list)

    # Financial Impact
    estimated_undervaluation: Optional[float] = None
    estimated_duty_evasion: Optional[float] = None

    # Recommendations
    recommended_actions: List[str] = Field(default_factory=list)
    investigation_priority: str = Field(...,
                                        description="LOW, MEDIUM, HIGH, URGENT")

    # Summary
    executive_summary: str
    technical_details: Dict[str, Any] = Field(default_factory=dict)


class AgentStep(BaseModel):
    """Individual step in the ReAct agent execution."""
    step_number: int
    step_type: str = Field(..., description="OBSERVATION, THOUGHT, ACTION")
    content: str
    tool_used: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: Optional[int] = None


class AgentExecution(BaseModel):
    """Complete agent execution trace."""
    execution_id: str
    bundle_id: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    status: str = Field(default="running",
                        description="running, completed, failed, timeout")

    # Execution trace
    steps: List[AgentStep] = Field(default_factory=list)
    total_steps: int = 0

    # Performance metrics
    total_duration_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    api_calls_made: int = 0

    # Results
    fraud_analysis: Optional[FraudAnalysisResult] = None
    error_message: Optional[str] = None

    def add_step(self, step_type: str, content: str, tool_used: Optional[str] = None,
                 tool_input: Optional[Dict[str, Any]] = None, tool_output: Optional[str] = None) -> AgentStep:
        """Add a new step to the execution trace."""
        step = AgentStep(
            step_number=len(self.steps) + 1,
            step_type=step_type,
            content=content,
            tool_used=tool_used,
            tool_input=tool_input,
            tool_output=tool_output
        )
        self.steps.append(step)
        self.total_steps = len(self.steps)
        return step

    def complete_execution(self, fraud_analysis: FraudAnalysisResult):
        """Mark execution as completed with results."""
        self.end_time = datetime.utcnow()
        self.status = "completed"
        self.fraud_analysis = fraud_analysis
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.total_duration_ms = int(delta.total_seconds() * 1000)

    def fail_execution(self, error_message: str):
        """Mark execution as failed with error message."""
        self.end_time = datetime.utcnow()
        self.status = "failed"
        self.error_message = error_message
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.total_duration_ms = int(delta.total_seconds() * 1000)
