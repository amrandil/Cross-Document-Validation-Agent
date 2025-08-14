"""Executor wrapper for the fraud detection agent."""

import asyncio
import json
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

    async def execute_fraud_analysis_stream(self, bundle: DocumentBundle, options: Optional[Dict[str, Any]] = None, stream_queue: asyncio.Queue = None):
        """Execute fraud analysis with real-time streaming updates.

        Args:
            bundle: Document bundle to analyze
            options: Optional analysis options
            stream_queue: Queue for sending streaming updates

        Returns:
            AgentExecution: Complete execution trace with results
        """
        try:
            logger.info(
                f"Starting streaming fraud analysis for bundle {bundle.bundle_id}")

            # Validate bundle
            self._validate_bundle(bundle)

            # Execute streaming analysis using agent
            execution = await self.agent.analyze_documents_stream(bundle, options, stream_queue)

            logger.info(
                f"Streaming fraud analysis completed: {execution.execution_id}")
            return execution

        except Exception as e:
            logger.error(f"Streaming fraud analysis failed: {str(e)}")
            if stream_queue:
                await stream_queue.put({
                    "type": "error",
                    "message": f"Analysis failed: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                })
            raise AgentExecutionError(
                f"Failed to execute streaming fraud analysis: {str(e)}",
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
        # Collect LLMs from known components to avoid frontend hardcoding
        from ..utils.vision_pdf_processor import VisionPDFProcessor
        vision_info = VisionPDFProcessor().get_processor_info()

        llms_used = []
        if vision_info.get("vision_model"):
            llms_used.append({
                "name": vision_info["vision_model"],
                "role": "Vision PDF Extraction"
            })
        if vision_info.get("summary_model"):
            llms_used.append({
                "name": vision_info["summary_model"],
                "role": "Document Summary"
            })

        return {
            "agent_type": "FraudDetectionAgent",
            "tools_count": len(self.agent.tools),
            "tools": [tool.name for tool in self.agent.tools],
            "llms_used": llms_used,
        }
