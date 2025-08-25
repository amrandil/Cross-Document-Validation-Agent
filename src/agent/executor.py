"""Executor wrapper for the fraud detection agent."""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

from .react_agent import ReActFraudDetectionAgent
from ..models.documents import DocumentBundle
from ..models.fraud import AgentExecution
from ..utils.logging_config import workflow_logger
from ..utils.exceptions import AgentExecutionError

logger = workflow_logger.logger


class FraudDetectionExecutor:
    """High-level executor for fraud detection operations."""

    def __init__(self):
        # Initialize ReAct agent
        self.react_agent = ReActFraudDetectionAgent()

        # Don't initialize old agent here to avoid import issues
        self.agent = None
        self.old_agent_available = None  # Will be checked lazily
        logger.info("Initialized FraudDetectionExecutor with ReAct agent")

    def _get_old_agent(self):
        """Lazily load the old agent if available."""
        if self.old_agent_available is None:
            try:
                from .core import FraudDetectionAgent
                self.agent = FraudDetectionAgent()
                self.old_agent_available = True
                logger.info("Old agent loaded successfully")
            except ImportError as e:
                self.agent = None
                self.old_agent_available = False
                logger.info(f"Old agent not available: {e}")

        return self.agent if self.old_agent_available else None

    def execute_fraud_analysis(self, bundle: DocumentBundle, options: Optional[Dict[str, Any]] = None) -> AgentExecution:
        """Execute fraud analysis on a document bundle using the old fixed-phase agent.

        Args:
            bundle: Document bundle to analyze
            options: Optional analysis options

        Returns:
            AgentExecution: Complete execution trace with results

        Raises:
            AgentExecutionError: If execution fails
        """
        # Try to get old agent
        old_agent = self._get_old_agent()
        if not old_agent:
            raise AgentExecutionError(
                "Old agent not available. Use execute_react_fraud_analysis instead.",
                execution_id=None,
                details={"bundle_id": bundle.bundle_id}
            )

        try:
            logger.info(
                f"Starting fraud analysis execution for bundle {bundle.bundle_id}")

            # Validate bundle
            self._validate_bundle(bundle)

            # Execute analysis using agent
            execution = old_agent.analyze_documents(bundle, options)

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

    def execute_react_fraud_analysis(self, extracted_content: Dict[str, str], options: Optional[Dict[str, Any]] = None) -> AgentExecution:
        """Execute fraud analysis using the new ReAct agent.

        Args:
            extracted_content: Dictionary of filename -> extracted text content
            options: Optional analysis options

        Returns:
            AgentExecution: Complete execution trace with results

        Raises:
            AgentExecutionError: If execution fails
        """
        try:
            logger.info(
                f"Starting ReAct fraud analysis with {len(extracted_content)} documents")

            # Validate extracted content
            self._validate_extracted_content(extracted_content)

            # Execute analysis using ReAct agent
            execution = self.react_agent.analyze_documents(
                extracted_content, options)

            logger.info(
                f"ReAct fraud analysis execution completed: {execution.execution_id}")
            return execution

        except Exception as e:
            logger.error(f"ReAct fraud analysis execution failed: {str(e)}")
            raise AgentExecutionError(
                f"Failed to execute ReAct fraud analysis: {str(e)}",
                execution_id=None,
                details={"document_count": len(
                    extracted_content), "error": str(e)}
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
        # Try to get old agent
        old_agent = self._get_old_agent()
        if not old_agent:
            raise AgentExecutionError(
                "Old agent not available. Streaming not supported with ReAct agent yet.",
                execution_id=None,
                details={"bundle_id": bundle.bundle_id}
            )

        try:
            logger.info(
                f"Starting streaming fraud analysis for bundle {bundle.bundle_id}")

            # Validate bundle
            self._validate_bundle(bundle)

            # Execute streaming analysis using agent
            execution = await old_agent.analyze_documents_stream(bundle, options, stream_queue)

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

    def _validate_extracted_content(self, extracted_content: Dict[str, str]):
        """Validate extracted content before ReAct analysis."""
        if not extracted_content:
            raise AgentExecutionError(
                "No extracted content provided",
                details={"document_count": 0}
            )

        # Check for minimum content
        for filename, content in extracted_content.items():
            if not content or len(content.strip()) < 10:
                raise AgentExecutionError(
                    f"Document {filename} has insufficient extracted content",
                    details={"filename": filename, "content_length": len(
                        content) if content else 0}
                )

        logger.info(
            f"Validated {len(extracted_content)} documents with extracted content")

    async def execute_react_fraud_analysis_stream(
        self,
        extracted_content: Dict[str, str],
        options: Optional[Dict[str, Any]] = None,
        stream_queue: Optional[asyncio.Queue] = None
    ) -> AgentExecution:
        """Execute streaming fraud analysis using ReAct agent."""

        try:
            # Validate extracted content
            self._validate_extracted_content(extracted_content)

            # Execute ReAct analysis with streaming updates
            execution = await self.react_agent.analyze_documents_stream(extracted_content, options, stream_queue)

            logger.info(
                f"ReAct streaming fraud analysis completed: {execution.execution_id}")
            return execution

        except Exception as e:
            logger.error(f"ReAct streaming fraud analysis failed: {str(e)}")
            if stream_queue:
                await stream_queue.put({
                    "type": "error",
                    "message": f"ReAct analysis failed: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                })
            raise AgentExecutionError(
                f"Failed to execute ReAct streaming fraud analysis: {str(e)}",
                execution_id=None,
                details={"document_count": len(
                    extracted_content), "error": str(e)}
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
            "old_agent_available": self.old_agent_available if self.old_agent_available is not None else False,
            "react_agent_available": True,
            "tools_count": len(self.react_agent.actor.tools) if hasattr(self.react_agent, 'actor') else 0,
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

                        # Update the ReAct agent's model
                        self.react_agent.llm = test_llm
                        self.react_agent.observer.llm = test_llm
                        self.react_agent.thinker.llm = test_llm
                        self.react_agent.actor.llm = test_llm

                        # Update old agent if available
                        old_agent = self._get_old_agent()
                        if old_agent:
                            old_agent.llm = test_llm

                        settings.openai_model = new_model  # Update settings
                        updated_models.append({
                            "role": "Main Reasoning Agent",
                            "old_model": old_model,
                            "new_model": new_model
                        })
                        logger.info(
                            f"Updated main reasoning agent model to: {new_model}")

                    except Exception as e:
                        error_msg = f"Invalid model '{new_model}' for Main Reasoning Agent: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)

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
                        logger.info(
                            f"Updated vision model from {old_model} to: {new_model}")
                    except Exception as e:
                        error_msg = f"Invalid model '{new_model}' for Vision PDF Extraction: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)

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
                        logger.info(
                            f"Updated summary model from {old_model} to: {new_model}")
                    except Exception as e:
                        error_msg = f"Invalid model '{new_model}' for Document Summary: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)

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
            logger.error(f"Error in update_models: {str(e)}")
            raise
