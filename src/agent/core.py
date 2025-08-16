"""Core ReAct fraud detection agent implementation."""

import uuid
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
# Remove unused langchain agents imports - we use custom ReAct implementation
from langchain_openai import ChatOpenAI

from .prompts import get_agent_prompt_template
from .memory import FraudDetectionMemory
from ..tools import get_all_tools
from ..models.documents import DocumentBundle
from ..models.fraud import FraudAnalysisResult, AgentExecution, FraudIndicator, FraudType
from ..config import settings
from ..utils.exceptions import AgentExecutionError


class FraudDetectionAgent:
    """Multi-Document Fraud Detection Agent using ReAct strategy."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )

        # Get all fraud detection tools
        self.tools = get_all_tools()
        self.tool_names = [tool.name for tool in self.tools]

        # Create agent prompt template
        self.prompt_template = get_agent_prompt_template()

    def analyze_documents(self, bundle: DocumentBundle, options: Optional[Dict[str, Any]] = None) -> AgentExecution:
        """Analyze a document bundle for fraud using ReAct strategy."""

        execution_id = str(uuid.uuid4())
        options = options or {}

        # Initialize memory and tracking
        memory = FraudDetectionMemory(execution_id, bundle.bundle_id)

        try:
            # Phase 1: Initial Observation
            memory.set_phase("initial_observation")
            initial_observation = self._conduct_initial_observation(bundle)
            memory.add_observation(initial_observation)

            # Phase 2: Document Extraction
            memory.set_phase("document_extraction")
            extracted_data = self._extract_document_data(bundle, memory)
            memory.update_context("extracted_data", extracted_data)

            # Phase 3: Systematic Validation
            memory.set_phase("systematic_validation")
            validation_results = self._conduct_systematic_validation(
                bundle, memory, extracted_data)

            # Phase 4: Advanced Pattern Detection
            memory.set_phase("pattern_detection")
            pattern_results = self._conduct_pattern_detection(
                bundle, memory, extracted_data, validation_results)

            # Phase 5: Evidence Synthesis
            memory.set_phase("evidence_synthesis")
            fraud_analysis = self._synthesize_evidence(
                bundle, memory, extracted_data, validation_results + pattern_results)

            # Complete the execution
            memory.agent_execution.complete_execution(fraud_analysis)

            return memory.get_agent_execution()

        except Exception as e:
            memory.agent_execution.fail_execution(str(e))
            return memory.get_agent_execution()

    async def analyze_documents_stream(self, bundle: DocumentBundle, options: Optional[Dict[str, Any]] = None, stream_queue: asyncio.Queue = None) -> AgentExecution:
        """Analyze a document bundle for fraud with real-time streaming updates."""

        execution_id = str(uuid.uuid4())
        options = options or {}

        # Initialize memory and tracking
        memory = FraudDetectionMemory(execution_id, bundle.bundle_id)

        # Define phases for progress tracking
        phases = [
            ("initial_observation", "Initial Observation"),
            ("document_extraction", "Document Extraction"),
            ("systematic_validation", "Systematic Validation"),
            ("pattern_detection", "Pattern Detection"),
            ("evidence_synthesis", "Evidence Synthesis")
        ]

        try:
            await self._send_stream_update(stream_queue, {
                "type": "analysis_started",
                "execution_id": execution_id,
                "bundle_id": bundle.bundle_id,
                "total_phases": len(phases),
                "message": "Starting fraud analysis..."
            })

            # Phase 1: Initial Observation
            await self._send_phase_update(stream_queue, 1, "initial_observation", "Initial Observation", "Starting environmental assessment...")
            memory.set_phase("initial_observation")

            # Add detailed Phase 1 progress
            await self._send_step_update(stream_queue, memory, "THOUGHT", "Starting initial observation phase - assessing document bundle and environment...")

            initial_observation = self._conduct_initial_observation(bundle)
            memory.add_observation(initial_observation)
            await self._send_step_update(stream_queue, memory, "OBSERVATION", initial_observation)

            # Add Phase 1 completion message
            await self._send_step_update(stream_queue, memory, "THOUGHT", "Initial observation phase completed - environment assessed and ready for document extraction.")

            # Phase 2: Document Extraction
            await self._send_phase_update(stream_queue, 2, "document_extraction", "Document Extraction", "Extracting structured data from documents...")
            memory.set_phase("document_extraction")

            # Add detailed Phase 2 progress
            await self._send_step_update(stream_queue, memory, "THOUGHT", f"Starting document extraction phase - processing {len(bundle.documents)} documents...")

            extracted_data = await self._extract_document_data_stream(bundle, memory, stream_queue)
            memory.update_context("extracted_data", extracted_data)

            # Phase 3: Systematic Validation
            await self._send_phase_update(stream_queue, 3, "systematic_validation", "Systematic Validation", "Performing cross-document validations...")
            memory.set_phase("systematic_validation")
            validation_results = await self._conduct_systematic_validation_stream(
                bundle, memory, extracted_data, stream_queue)

            # Phase 4: Advanced Pattern Detection
            await self._send_phase_update(stream_queue, 4, "pattern_detection", "Pattern Detection", "Detecting sophisticated fraud patterns...")
            memory.set_phase("pattern_detection")
            pattern_results = await self._conduct_pattern_detection_stream(
                bundle, memory, extracted_data, validation_results, stream_queue)

            # Phase 5: Evidence Synthesis
            await self._send_phase_update(stream_queue, 5, "evidence_synthesis", "Evidence Synthesis", "Synthesizing evidence into final assessment...")
            memory.set_phase("evidence_synthesis")
            fraud_analysis = await self._synthesize_evidence_stream(
                bundle, memory, extracted_data, validation_results + pattern_results, stream_queue)

            # Complete the execution
            memory.agent_execution.complete_execution(fraud_analysis)

            await self._send_stream_update(stream_queue, {
                "type": "analysis_completed",
                "execution_id": execution_id,
                "bundle_id": bundle.bundle_id,
                "total_steps": len(memory.agent_execution.steps),
                "fraud_detected": fraud_analysis.fraud_detected,
                "risk_level": fraud_analysis.risk_level,
                "message": "Analysis completed successfully"
            })

            return memory.get_agent_execution()

        except Exception as e:
            memory.agent_execution.fail_execution(str(e))

            await self._send_stream_update(stream_queue, {
                "type": "analysis_error",
                "execution_id": execution_id,
                "bundle_id": bundle.bundle_id,
                "error": str(e),
                "message": "Analysis failed"
            })

            return memory.get_agent_execution()

    async def _send_stream_update(self, stream_queue: asyncio.Queue, update: Dict[str, Any]):
        """Send an update to the stream queue."""
        if stream_queue:
            update["timestamp"] = datetime.utcnow().isoformat()
            await stream_queue.put(update)

    async def _send_phase_update(self, stream_queue: asyncio.Queue, phase_number: int, phase_id: str, phase_name: str, message: str):
        """Send a phase update to the stream."""
        await self._send_stream_update(stream_queue, {
            "type": "phase_started",
            "phase_number": phase_number,
            "phase_id": phase_id,
            "phase_name": phase_name,
            "message": message
        })

    async def _send_step_update(self, stream_queue: asyncio.Queue, memory: FraudDetectionMemory, step_type: str, content: str):
        """Send a step update to the stream."""
        step = memory.add_step(step_type, content)
        await self._send_stream_update(stream_queue, {
            "type": "step_completed",
            "step_number": step.step_number,
            "step_type": step.step_type,
            "content": step.content,
            "tool_used": step.tool_used,
            "tool_output": step.tool_output,
            "timestamp": step.timestamp.isoformat(),
            "total_steps": len(memory.agent_execution.steps)
        })

    async def _send_action_step_update(self, stream_queue: asyncio.Queue, memory: FraudDetectionMemory, content: str, tool_used: str, tool_input: Dict[str, Any], tool_output: str):
        """Send an action step update with tool information to the stream."""
        step = memory.add_action(content, tool_used, tool_input, tool_output)
        await self._send_stream_update(stream_queue, {
            "type": "step_completed",
            "step_number": step.step_number,
            "step_type": step.step_type,
            "content": step.content,
            "tool_used": step.tool_used,
            "tool_output": step.tool_output,
            "timestamp": step.timestamp.isoformat(),
            "total_steps": len(memory.agent_execution.steps)
        })

    async def _extract_document_data_stream(self, bundle: DocumentBundle, memory: FraudDetectionMemory, stream_queue: asyncio.Queue) -> Dict[str, Any]:
        """Extract structured data from all documents with streaming updates."""
        await self._send_step_update(stream_queue, memory, "THOUGHT",
                                     "I need to extract structured data from all documents to enable cross-document analysis. This is the foundation for all fraud detection.")

        # Use document extraction tool
        extraction_tool = next(
            tool for tool in self.tools if tool.name == "extract_data_from_document")

        bundle_data = {
            "bundle_id": bundle.bundle_id,
            "documents": [
                {
                    "document_type": doc.document_type.value,
                    "filename": doc.filename,
                    "content": doc.content
                }
                for doc in bundle.documents
            ]
        }

        await self._send_action_step_update(stream_queue, memory,
                                            "Extracting structured data from all documents", "extract_data_from_document", bundle_data, "Processing...")

        # Add progress updates for each document
        for i, doc in enumerate(bundle.documents, 1):
            await self._send_stream_update(stream_queue, {
                "type": "tool_progress",
                "tool_name": "extract_data_from_document",
                "tool_number": i,
                "total_tools": len(bundle.documents),
                "message": f"Processing document {i}/{len(bundle.documents)}: {doc.filename}"
            })

        # Run the extraction tool (this is the slow part)
        # Use asyncio.to_thread to run the synchronous tool in a thread pool
        result = await asyncio.to_thread(extraction_tool._run, bundle_data=bundle_data)

        await self._send_action_step_update(stream_queue, memory,
                                            "Extracting structured data from all documents", "extract_data_from_document", bundle_data, result)

        # Parse and store extracted data
        extracted_data = {"extraction_summary": result}
        memory.update_context("extracted_data", extracted_data)

        # Add Phase 2 completion message
        await self._send_step_update(stream_queue, memory, "THOUGHT", f"Document extraction phase completed - extracted structured data from {len(bundle.documents)} documents.")

        return extracted_data

    async def _conduct_systematic_validation_stream(self, bundle: DocumentBundle, memory: FraudDetectionMemory,
                                                    extracted_data: Dict[str, Any], stream_queue: asyncio.Queue) -> List[str]:
        """Conduct systematic cross-document validation with streaming updates."""
        await self._send_step_update(stream_queue, memory, "THOUGHT",
                                     "Now I'll perform systematic cross-document validation to identify inconsistencies that could indicate fraud.")

        validation_results = []

        # Get validation tools
        validation_tools = [
            "validate_quantity_consistency",
            "validate_weight_consistency",
            "validate_entity_consistency",
            "validate_product_descriptions",
            "validate_value_consistency",
            "validate_geographic_consistency"
        ]

        for i, tool_name in enumerate(validation_tools, 1):
            try:
                await self._send_stream_update(stream_queue, {
                    "type": "tool_progress",
                    "tool_name": tool_name,
                    "tool_number": i,
                    "total_tools": len(validation_tools),
                    "message": f"Running {tool_name.replace('_', ' ')}..."
                })

                tool = next(
                    tool for tool in self.tools if tool.name == tool_name)

                await self._send_step_update(stream_queue, memory, "THOUGHT",
                                             f"Running {tool_name} to check for cross-document inconsistencies.")

                bundle_data = {
                    "bundle_id": bundle.bundle_id,
                    "documents": [
                        {
                            "document_type": doc.document_type.value,
                            "filename": doc.filename,
                            "content": doc.content
                        }
                        for doc in bundle.documents
                    ]
                }

                tool_options = {"extracted_data": extracted_data}
                result = await asyncio.to_thread(tool._run, bundle_data=bundle_data,
                                                 options=tool_options)

                await self._send_action_step_update(stream_queue, memory,
                                                    f"Validating {tool_name.replace('validate_', '').replace('_', ' ')}",
                                                    tool_name, {"bundle_data": bundle_data, "options": tool_options}, result)

                validation_results.append(result)
                memory.add_analysis_result(result)

            except Exception as e:
                await self._send_step_update(stream_queue, memory, "OBSERVATION", f"Error in {tool_name}: {str(e)}")

        return validation_results

    async def _conduct_pattern_detection_stream(self, bundle: DocumentBundle, memory: FraudDetectionMemory,
                                                extracted_data: Dict[str, Any], validation_results: List[str], stream_queue: asyncio.Queue) -> List[str]:
        """Conduct advanced pattern detection with streaming updates."""
        await self._send_step_update(stream_queue, memory, "THOUGHT",
                                     "Moving to advanced pattern detection to identify sophisticated fraud schemes that might not be obvious from basic validation.")

        pattern_results = []

        # Get pattern detection tools
        pattern_tools = [
            "detect_product_substitution",
            "detect_origin_manipulation",
            "detect_entity_variations",
            "validate_unit_calculations",
            "detect_round_number_patterns"
        ]

        for i, tool_name in enumerate(pattern_tools, 1):
            try:
                await self._send_stream_update(stream_queue, {
                    "type": "tool_progress",
                    "tool_name": tool_name,
                    "tool_number": i,
                    "total_tools": len(pattern_tools),
                    "message": f"Running {tool_name.replace('_', ' ')}..."
                })

                tool = next(
                    (tool for tool in self.tools if tool.name == tool_name), None)
                if not tool:
                    continue

                await self._send_step_update(stream_queue, memory, "THOUGHT",
                                             f"Applying {tool_name} to detect sophisticated fraud patterns.")

                bundle_data = {
                    "bundle_id": bundle.bundle_id,
                    "documents": [
                        {
                            "document_type": doc.document_type.value,
                            "filename": doc.filename,
                            "content": doc.content
                        }
                        for doc in bundle.documents
                    ]
                }

                tool_options = {
                    "extracted_data": extracted_data,
                    "validation_results": validation_results
                }
                result = await asyncio.to_thread(tool._run, bundle_data=bundle_data,
                                                 options=tool_options)

                await self._send_action_step_update(stream_queue, memory,
                                                    f"Detecting {tool_name.replace('detect_', '').replace('validate_', '').replace('_', ' ')} patterns",
                                                    tool_name, {"bundle_data": bundle_data, "options": tool_options}, result)

                pattern_results.append(result)
                memory.add_analysis_result(result)

            except Exception as e:
                await self._send_step_update(stream_queue, memory, "OBSERVATION", f"Error in {tool_name}: {str(e)}")

        return pattern_results

    async def _synthesize_evidence_stream(self, bundle: DocumentBundle, memory: FraudDetectionMemory,
                                          extracted_data: Dict[str, Any], all_results: List[str], stream_queue: asyncio.Queue) -> FraudAnalysisResult:
        """Synthesize all evidence with streaming updates."""
        await self._send_step_update(stream_queue, memory, "THOUGHT",
                                     "Synthesizing all analysis results into a comprehensive fraud assessment with overall confidence and recommendations.")

        try:
            # Use evidence synthesis tool
            synthesis_tool = next(
                tool for tool in self.tools if tool.name == "synthesize_fraud_evidence")

            bundle_data = {
                "bundle_id": bundle.bundle_id,
                "documents": [
                    {
                        "document_type": doc.document_type.value,
                        "filename": doc.filename,
                        "content": doc.content
                    }
                    for doc in bundle.documents
                ]
            }

            tool_options = {
                "extracted_data": extracted_data,
                "analysis_results": all_results
            }

            await self._send_action_step_update(stream_queue, memory,
                                                "Synthesizing all fraud evidence into comprehensive assessment", "synthesize_fraud_evidence",
                                                {"bundle_data": bundle_data, "options": tool_options}, "Processing...")

            synthesis_result = await asyncio.to_thread(synthesis_tool._run,
                                                       bundle_data=bundle_data, options=tool_options)

            await self._send_action_step_update(stream_queue, memory,
                                                "Synthesizing all fraud evidence into comprehensive assessment", "synthesize_fraud_evidence",
                                                {"bundle_data": bundle_data, "options": tool_options}, synthesis_result)

            # Create structured fraud analysis result
            fraud_analysis = self._parse_synthesis_result(
                bundle.bundle_id, synthesis_result, all_results)

            return fraud_analysis

        except Exception as e:
            await self._send_step_update(stream_queue, memory, "OBSERVATION", f"Error in evidence synthesis: {str(e)}")
            # Create fallback fraud analysis
            return self._create_fallback_analysis(bundle.bundle_id, all_results, str(e))

    def _conduct_initial_observation(self, bundle: DocumentBundle) -> str:
        """Conduct initial observation of the document bundle."""
        observation_parts = []
        observation_parts.append(
            "INITIAL OBSERVATION - ENVIRONMENTAL ASSESSMENT")
        observation_parts.append("=" * 50)

        # Document bundle assessment
        doc_types = bundle.get_document_types()
        observation_parts.append(
            f"Document Bundle: {len(bundle.documents)} documents received")
        for doc_type in doc_types:
            doc = bundle.get_document_by_type(doc_type)
            if doc:
                observation_parts.append(
                    f"  - {doc_type.value}: {doc.filename}")

        # Required documents check
        has_required = bundle.has_required_documents()
        observation_parts.append(
            f"Required Documents Present: {'✅ YES' if has_required else '❌ NO'}")

        # Basic risk assessment from document analysis
        risk_indicators = []

        # Check for completeness
        if not has_required:
            risk_indicators.append("Missing required documents")

        # Check document count
        if len(bundle.documents) > 5:
            risk_indicators.append("Complex document bundle")

        observation_parts.append(
            f"Initial Risk Assessment: {len(risk_indicators)} indicators identified")
        for indicator in risk_indicators:
            observation_parts.append(f"  - {indicator}")

        observation_parts.append(
            "\nENVIRONMENT ASSESSED - READY FOR DOCUMENT EXTRACTION")

        return "\n".join(observation_parts)

    def _extract_document_data(self, bundle: DocumentBundle, memory: FraudDetectionMemory) -> Dict[str, Any]:
        """Extract structured data from all documents."""
        memory.add_thought(
            "I need to extract structured data from all documents to enable cross-document analysis. This is the foundation for all fraud detection.")

        # Use document extraction tool
        extraction_tool = next(
            tool for tool in self.tools if tool.name == "extract_data_from_document")

        bundle_data = {
            "bundle_id": bundle.bundle_id,
            "documents": [
                {
                    "document_type": doc.document_type.value,
                    "filename": doc.filename,
                    "content": doc.content
                }
                for doc in bundle.documents
            ]
        }

        tool_input = {"bundle_data": bundle_data}
        result = extraction_tool._run(bundle_data=bundle_data)

        memory.add_action(
            "Extracting structured data from all documents",
            "extract_data_from_document",
            tool_input,
            result
        )

        # Parse and store extracted data (simplified for MVP)
        extracted_data = {"extraction_summary": result}
        memory.update_context("extracted_data", extracted_data)

        return extracted_data

    def _conduct_systematic_validation(self, bundle: DocumentBundle, memory: FraudDetectionMemory,
                                       extracted_data: Dict[str, Any]) -> List[str]:
        """Conduct systematic cross-document validation."""
        memory.add_thought(
            "Now I'll perform systematic cross-document validation to identify inconsistencies that could indicate fraud.")

        validation_results = []

        # Get validation tools
        validation_tools = [
            "validate_quantity_consistency",
            "validate_weight_consistency",
            "validate_entity_consistency",
            "validate_product_descriptions",
            "validate_value_consistency",
            "validate_geographic_consistency"
        ]

        for tool_name in validation_tools:
            try:
                tool = next(
                    tool for tool in self.tools if tool.name == tool_name)

                memory.add_thought(
                    f"Running {tool_name} to check for cross-document inconsistencies.")

                bundle_data = {
                    "bundle_id": bundle.bundle_id,
                    "documents": [
                        {
                            "document_type": doc.document_type.value,
                            "filename": doc.filename,
                            "content": doc.content
                        }
                        for doc in bundle.documents
                    ]
                }

                tool_options = {"extracted_data": extracted_data}
                result = tool._run(bundle_data=bundle_data,
                                   options=tool_options)

                memory.add_action(
                    f"Validating {tool_name.replace('validate_', '').replace('_', ' ')}",
                    tool_name,
                    {"bundle_data": bundle_data, "options": tool_options},
                    result
                )

                validation_results.append(result)
                memory.add_analysis_result(result)

            except Exception as e:
                memory.add_observation(f"Error in {tool_name}: {str(e)}")

        return validation_results

    def _conduct_pattern_detection(self, bundle: DocumentBundle, memory: FraudDetectionMemory,
                                   extracted_data: Dict[str, Any], validation_results: List[str]) -> List[str]:
        """Conduct advanced pattern detection for sophisticated fraud schemes."""
        memory.add_thought(
            "Moving to advanced pattern detection to identify sophisticated fraud schemes that might not be obvious from basic validation.")

        pattern_results = []

        # Get pattern detection tools
        pattern_tools = [
            "detect_product_substitution",
            "detect_origin_manipulation",
            "detect_entity_variations",
            "validate_unit_calculations",
            "detect_round_number_patterns"
        ]

        for tool_name in pattern_tools:
            try:
                tool = next(
                    (tool for tool in self.tools if tool.name == tool_name), None)
                if not tool:
                    continue

                memory.add_thought(
                    f"Applying {tool_name} to detect sophisticated fraud patterns.")

                bundle_data = {
                    "bundle_id": bundle.bundle_id,
                    "documents": [
                        {
                            "document_type": doc.document_type.value,
                            "filename": doc.filename,
                            "content": doc.content
                        }
                        for doc in bundle.documents
                    ]
                }

                tool_options = {
                    "extracted_data": extracted_data,
                    "validation_results": validation_results
                }
                result = tool._run(bundle_data=bundle_data,
                                   options=tool_options)

                memory.add_action(
                    f"Detecting {tool_name.replace('detect_', '').replace('validate_', '').replace('_', ' ')} patterns",
                    tool_name,
                    {"bundle_data": bundle_data, "options": tool_options},
                    result
                )

                pattern_results.append(result)
                memory.add_analysis_result(result)

            except Exception as e:
                memory.add_observation(f"Error in {tool_name}: {str(e)}")

        return pattern_results

    def _synthesize_evidence(self, bundle: DocumentBundle, memory: FraudDetectionMemory,
                             extracted_data: Dict[str, Any], all_results: List[str]) -> FraudAnalysisResult:
        """Synthesize all evidence into comprehensive fraud assessment."""
        memory.add_thought(
            "Synthesizing all analysis results into a comprehensive fraud assessment with overall confidence and recommendations.")

        try:
            # Use evidence synthesis tool
            synthesis_tool = next(
                tool for tool in self.tools if tool.name == "synthesize_fraud_evidence")

            bundle_data = {
                "bundle_id": bundle.bundle_id,
                "documents": [
                    {
                        "document_type": doc.document_type.value,
                        "filename": doc.filename,
                        "content": doc.content
                    }
                    for doc in bundle.documents
                ]
            }

            tool_options = {
                "extracted_data": extracted_data,
                "analysis_results": all_results
            }

            synthesis_result = synthesis_tool._run(
                bundle_data=bundle_data, options=tool_options)

            memory.add_action(
                "Synthesizing all fraud evidence into comprehensive assessment",
                "synthesize_fraud_evidence",
                {"bundle_data": bundle_data, "options": tool_options},
                synthesis_result
            )

            # Create structured fraud analysis result
            fraud_analysis = self._parse_synthesis_result(
                bundle.bundle_id, synthesis_result, all_results)

            return fraud_analysis

        except Exception as e:
            # Create fallback fraud analysis
            return self._create_fallback_analysis(bundle.bundle_id, all_results, str(e))

    def _parse_synthesis_result(self, bundle_id: str, synthesis_result: str, all_results: List[str]) -> FraudAnalysisResult:
        """Parse synthesis result into structured fraud analysis."""
        # For MVP, create a basic structured result
        # In production, this would parse the LLM output more sophisticatedly

        analysis_id = str(uuid.uuid4())

        # Basic fraud detection based on keywords in results
        fraud_keywords = ["fraud detected", "suspicious",
                          "inconsistency", "discrepancy", "manipulation"]
        fraud_detected = any(keyword.lower() in result.lower()
                             for result in all_results for keyword in fraud_keywords)

        # Estimate confidence based on number of positive results
        positive_results = sum(1 for result in all_results if any(
            keyword.lower() in result.lower() for keyword in fraud_keywords))
        overall_confidence = min(
            positive_results / len(all_results) if all_results else 0.0, 1.0)

        # Determine risk level
        if overall_confidence >= 0.8:
            risk_level = "CRITICAL"
        elif overall_confidence >= 0.6:
            risk_level = "HIGH"
        elif overall_confidence >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return FraudAnalysisResult(
            bundle_id=bundle_id,
            analysis_id=analysis_id,
            fraud_detected=fraud_detected,
            overall_confidence=overall_confidence,
            risk_level=risk_level,
            investigation_priority="HIGH" if fraud_detected else "MEDIUM",
            executive_summary=synthesis_result,
            recommended_actions=[
                "Physical inspection recommended" if fraud_detected else "Standard processing",
                "Detailed investigation of identified inconsistencies" if fraud_detected else "Monitor for patterns"
            ]
        )

    def _create_fallback_analysis(self, bundle_id: str, all_results: List[str], error_message: str) -> FraudAnalysisResult:
        """Create fallback analysis when synthesis fails."""
        analysis_id = str(uuid.uuid4())

        return FraudAnalysisResult(
            bundle_id=bundle_id,
            analysis_id=analysis_id,
            fraud_detected=False,
            overall_confidence=0.0,
            risk_level="LOW",
            investigation_priority="LOW",
            executive_summary=f"Analysis completed with errors: {error_message}. Manual review recommended.",
            recommended_actions=[
                "Manual review of documents recommended due to analysis errors"]
        )
