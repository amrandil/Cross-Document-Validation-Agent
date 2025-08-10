"""Executor wrapper for the fraud detection agent."""

from typing import Dict, Any, Optional
from datetime import datetime

from .core import FraudDetectionAgent
from ..models.documents import DocumentBundle
from ..models.fraud import AgentExecution
from ..utils.logging import get_logger
from ..utils.exceptions import AgentExecutionError

logger = get_logger(__name__)


class FraudDetectionExecutor:
    """High-level executor for fraud detection operations."""

    def __init__(self):
        self.agent = FraudDetectionAgent()
        logger.info("Initialized FraudDetectionExecutor")

    def execute_fraud_analysis(self, bundle: DocumentBundle, options: Optional[Dict[str, Any]] = None) -> AgentExecution:
        """Execute fraud analysis on a document bundle.

        Args:
            bundle: Document bundle to analyze
            options: Optional analysis options

        Returns:
            AgentExecution: Complete execution trace with results

        Raises:
            AgentExecutionError: If execution fails
        """
        try:
            logger.info(
                f"Starting fraud analysis execution for bundle {bundle.bundle_id}")

            # Validate bundle
            self._validate_bundle(bundle)

            # Execute analysis using agent
            execution = self.agent.analyze_documents(bundle, options)

            logger.info(
                f"Fraud analysis execution completed: {execution.execution_id}")
            return execution

        except Exception as e:
            logger.error(f"Fraud analysis execution failed: {str(e)}")
            raise AgentExecutionError(
                f"Failed to execute fraud analysis: {str(e)}",
                execution_id=None,
                details={"bundle_id": bundle.bundle_id, "error": str(e)}
            )

    def _validate_bundle(self, bundle: DocumentBundle):
        """Validate document bundle before analysis."""
        if not bundle.documents:
            raise AgentExecutionError(
                "Document bundle is empty",
                details={"bundle_id": bundle.bundle_id}
            )

        if not bundle.has_required_documents():
            logger.warning(
                f"Bundle {bundle.bundle_id} missing required documents")
            # Don't fail - agent can still provide useful analysis

        # Check for minimum content
        for doc in bundle.documents:
            if not doc.content or len(doc.content.strip()) < 10:
                raise AgentExecutionError(
                    f"Document {doc.filename} has insufficient content",
                    details={"bundle_id": bundle.bundle_id,
                             "filename": doc.filename}
                )

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent and its capabilities."""
        return {
            "agent_type": "FraudDetectionAgent",
            "tools_count": len(self.agent.tools),
            "tools": [tool.name for tool in self.agent.tools],
            "supported_document_types": [
                "commercial_invoice",
                "packing_list",
                "bill_of_lading",
                "certificate_of_origin",
                "customs_declaration"
            ],
            "fraud_types_detected": [
                "valuation_fraud",
                "quantity_manipulation",
                "weight_manipulation",
                "origin_manipulation",
                "product_substitution",
                "entity_misrepresentation"
            ]
        }
