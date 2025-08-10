"""Core ReAct fraud detection agent implementation."""

import uuid
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
from ..utils.logging import get_logger
from ..utils.exceptions import AgentExecutionError

logger = get_logger(__name__)


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

        logger.info(
            f"Initialized FraudDetectionAgent with {len(self.tools)} tools")

    def analyze_documents(self, bundle: DocumentBundle, options: Optional[Dict[str, Any]] = None) -> AgentExecution:
        """Analyze a document bundle for fraud using ReAct strategy."""

        execution_id = str(uuid.uuid4())
        options = options or {}

        # Initialize memory and tracking
        memory = FraudDetectionMemory(execution_id, bundle.bundle_id)

        try:
            logger.info(
                f"Starting fraud analysis for bundle {bundle.bundle_id}")

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

            logger.info(
                f"Completed fraud analysis for bundle {bundle.bundle_id}")
            return memory.get_agent_execution()

        except Exception as e:
            logger.error(f"Error in fraud analysis: {str(e)}")
            memory.agent_execution.fail_execution(str(e))
            return memory.get_agent_execution()

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
                logger.error(f"Error in {tool_name}: {str(e)}")
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
                logger.error(f"Error in {tool_name}: {str(e)}")
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
            logger.error(f"Error in evidence synthesis: {str(e)}")
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
