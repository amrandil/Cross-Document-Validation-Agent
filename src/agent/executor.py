"""Executor wrapper for the fraud detection agent."""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

from .core import FraudDetectionAgent
from ..models.documents import DocumentBundle
from ..models.fraud import AgentExecution
from ..utils.exceptions import AgentExecutionError


class FraudDetectionExecutor:
    """High-level executor for fraud detection operations."""

    def __init__(self):
        self.agent = FraudDetectionAgent()

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
            # Validate bundle
            self._validate_bundle(bundle)

            # Execute analysis using agent
            execution = self.agent.analyze_documents(bundle, options)

            return execution

        except Exception as e:
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
            # Validate bundle
            self._validate_bundle(bundle)

            # Execute streaming analysis using agent
            execution = await self.agent.analyze_documents_stream(bundle, options, stream_queue)

            return execution

        except Exception as e:
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
            pass  # Don't fail - agent can still provide useful analysis

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
        from ..config import settings
        from ..utils.vision_pdf_processor import VisionPDFProcessor

        # Collect LLMs from known components to avoid frontend hardcoding
        vision_info = VisionPDFProcessor.get_instance().get_processor_info()

        llms_used = []

        # Add main agent LLM
        llms_used.append({
            "name": settings.openai_model,
            "role": "Main Reasoning Agent"
        })

        # Add vision processor LLMs
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

    async def update_models(self, model_configs: Dict[str, str]) -> Dict[str, Any]:
        """Update the language models used by the agent."""
        from ..config import settings
        from ..utils.vision_pdf_processor import VisionPDFProcessor
        from langchain_openai import ChatOpenAI

        updated_models = []
        errors = []

        try:
            # Update main reasoning agent model
            if "main_reasoning_agent" in model_configs:
                new_model = model_configs["main_reasoning_agent"]
                old_model = settings.openai_model
                if new_model != old_model:
                    # Test the model by creating a ChatOpenAI instance
                    try:
                        test_llm = ChatOpenAI(
                            model=new_model,
                            temperature=settings.openai_temperature,
                            api_key=settings.openai_api_key
                        )
                        # Test with a simple call
                        await test_llm.ainvoke("Test message")

                        # Update the agent's model
                        self.agent.llm = test_llm
                        settings.openai_model = new_model  # Update settings
                        updated_models.append({
                            "role": "Main Reasoning Agent",
                            "old_model": old_model,
                            "new_model": new_model
                        })

                    except Exception as e:
                        error_msg = f"Invalid model '{new_model}' for Main Reasoning Agent: {str(e)}"
                        errors.append(error_msg)

            # Update vision processor models
            vision_processor = VisionPDFProcessor.get_instance()
            vision_info = vision_processor.get_processor_info()

            if "vision_pdf_extraction" in model_configs:
                new_model = model_configs["vision_pdf_extraction"]
                old_model = vision_info.get("vision_model", "unknown")
                if new_model != old_model:
                    try:
                        vision_processor.update_vision_model(new_model)
                        updated_models.append({
                            "role": "Vision PDF Extraction",
                            "old_model": old_model,
                            "new_model": new_model
                        })

                    except Exception as e:
                        error_msg = f"Invalid model '{new_model}' for Vision PDF Extraction: {str(e)}"
                        errors.append(error_msg)

            if "document_summary" in model_configs:
                new_model = model_configs["document_summary"]
                old_model = vision_info.get("summary_model", "unknown")
                if new_model != old_model:
                    try:
                        vision_processor.update_summary_model(new_model)
                        updated_models.append({
                            "role": "Document Summary",
                            "old_model": old_model,
                            "new_model": new_model
                        })

                    except Exception as e:
                        error_msg = f"Invalid model '{new_model}' for Document Summary: {str(e)}"
                        errors.append(error_msg)

            # Return results
            if errors and not updated_models:
                raise ValueError(
                    f"All model updates failed: {'; '.join(errors)}")

            result = {
                "success": True,
                "updated_models": updated_models,
                "message": f"Successfully updated {len(updated_models)} model(s)"
            }

            if errors:
                result["warnings"] = errors
                result["message"] += f" with {len(errors)} error(s)"

            return result

        except Exception as e:
            raise
