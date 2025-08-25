"""True ReAct agent implementation for fraud detection."""

import uuid
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from langchain_openai import ChatOpenAI

from .memory import FraudDetectionMemory
from ..models.fraud import AgentExecution, AgentStep, FraudAnalysisResult
from ..models.documents import DocumentBundle
from ..tools import get_all_tools
from ..config import settings
from ..utils.logging_config import workflow_logger
from ..utils.exceptions import AgentExecutionError

logger = workflow_logger.logger


@dataclass
class Observation:
    """Observation of current investigation state."""
    total_documents: int
    document_types: Dict[str, str]
    document_filenames: List[str]
    content_summary: str
    key_entities: Dict[str, List[str]]
    investigation_scope: str
    risk_indicators: List[str]
    available_tools: List[str]
    investigation_strategy: str
    fraud_indicators: List[str] = None
    evidence_collected: List[str] = None
    tools_executed: List[str] = None
    iteration_count: int = 0
    confidence_level: float = 0.0


@dataclass
class Reasoning:
    """Reasoning about next actions."""
    content: str
    recommended_action: str
    confidence: float
    reasoning_type: str  # "investigation", "validation", "synthesis"


@dataclass
class Action:
    """Action taken by the agent."""
    tool_name: str
    reasoning: Reasoning
    result: str
    timestamp: datetime


class Observer:
    """Observes the current investigation state."""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.logger = workflow_logger.logger

    def observe(self, extracted_content: Dict[str, str], memory: FraudDetectionMemory) -> Observation:
        """Analyze current investigation state and extracted content."""

        try:
            # Document inventory
            total_documents = len(extracted_content)
            document_types = self.identify_document_types(extracted_content)
            document_filenames = list(extracted_content.keys())

            # Content analysis
            content_summary = self.analyze_content_overview(extracted_content)
            key_entities = self.extract_key_entities(extracted_content)

            # Investigation context
            investigation_scope = self.assess_investigation_scope(
                extracted_content, document_types)
            risk_indicators = self.identify_initial_risk_indicators(
                extracted_content, document_types)

            # Current investigation state
            fraud_indicators = memory.get_fraud_indicators() if memory else []
            evidence_collected = memory.get_evidence() if memory else []
            tools_executed = memory.get_executed_tools() if memory else []
            iteration_count = memory.get_iteration_count() if memory else 0
            confidence_level = memory.get_confidence_level() if memory else 0.0

            # Available actions
            available_tools = self.get_available_tools()
            investigation_strategy = self.suggest_initial_strategy(
                extracted_content, document_types)

            return Observation(
                total_documents=total_documents,
                document_types=document_types,
                document_filenames=document_filenames,
                content_summary=content_summary,
                key_entities=key_entities,
                investigation_scope=investigation_scope,
                risk_indicators=risk_indicators,
                available_tools=available_tools,
                investigation_strategy=investigation_strategy,
                fraud_indicators=fraud_indicators,
                evidence_collected=evidence_collected,
                tools_executed=tools_executed,
                iteration_count=iteration_count,
                confidence_level=confidence_level
            )

        except Exception as e:
            self.logger.error(f"Error in observation: {str(e)}")
            raise AgentExecutionError(f"Observation failed: {str(e)}")

    def identify_document_types(self, extracted_content: Dict[str, str]) -> Dict[str, str]:
        """Identify document types from extracted content."""
        document_types = {}

        for filename, content in extracted_content.items():
            doc_type = self.classify_document_type(filename, content)
            document_types[filename] = doc_type

        return document_types

    def classify_document_type(self, filename: str, content: str) -> str:
        """Classify document type based on filename and content."""

        prompt = f"""
        Classify this document based on its filename and content.
        
        Filename: {filename}
        Content: {content[:1000]}...
        
        Document types to choose from:
        - commercial_invoice
        - packing_list  
        - bill_of_lading
        - certificate_of_origin
        - customs_declaration
        - other
        
        Return only the document type name.
        """

        try:
            response = self.llm.invoke(prompt)
            return response.content.strip().lower()
        except Exception as e:
            self.logger.warning(
                f"Could not classify document {filename}: {str(e)}")
            return "other"

    def analyze_content_overview(self, extracted_content: Dict[str, str]) -> str:
        """Analyze overall content to understand the shipment."""

        prompt = f"""
        Analyze these extracted document contents to understand the shipment.
        
        Documents:
        {self.format_documents_for_analysis(extracted_content)}
        
        Provide a brief overview including:
        - What type of shipment this appears to be
        - Key products/commodities involved
        - Approximate value range
        - Origin and destination countries
        - Any obvious characteristics or patterns
        
        Keep it concise and factual.
        """

        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            self.logger.warning(
                f"Could not analyze content overview: {str(e)}")
            return "Content analysis failed"

    def format_documents_for_analysis(self, extracted_content: Dict[str, str]) -> str:
        """Format documents for analysis prompt."""
        formatted = []
        for filename, content in extracted_content.items():
            formatted.append(f"File: {filename}")
            formatted.append(f"Content: {content[:500]}...")
            formatted.append("---")
        return "\n".join(formatted)

    def extract_key_entities(self, extracted_content: Dict[str, str]) -> Dict[str, List[str]]:
        """Extract key entities from documents."""

        entities = {
            "suppliers": [],
            "buyers": [],
            "products": [],
            "countries": [],
            "values": []
        }

        # For now, return basic structure - can be enhanced with LLM extraction
        return entities

    def assess_investigation_scope(self, extracted_content: Dict[str, str], document_types: Dict[str, str]) -> str:
        """Assess the scope and complexity of the investigation."""

        total_docs = len(extracted_content)
        doc_type_list = list(document_types.values())

        # Check for required documents
        required_docs = ["commercial_invoice",
                         "packing_list", "bill_of_lading"]
        has_required = all(
            doc_type in doc_type_list for doc_type in required_docs)

        scope_assessment = f"""
        INVESTIGATION SCOPE:
        - Total documents: {total_docs}
        - Document types: {doc_type_list}
        - Required documents present: {'YES' if has_required else 'NO'}
        - Investigation complexity: {'HIGH' if total_docs > 3 else 'MEDIUM' if total_docs > 1 else 'LOW'}
        """

        return scope_assessment

    def identify_initial_risk_indicators(self, extracted_content: Dict[str, str], document_types: Dict[str, str]) -> List[str]:
        """Identify initial risk indicators from document overview."""

        risk_indicators = []

        # Check for missing required documents
        required_docs = ["commercial_invoice",
                         "packing_list", "bill_of_lading"]
        doc_type_list = list(document_types.values())
        if not all(doc_type in doc_type_list for doc_type in required_docs):
            risk_indicators.append("Missing required documents")

        # Check for high document count (complex shipment)
        if len(extracted_content) > 4:
            risk_indicators.append("Complex document bundle")

        return risk_indicators

    def get_available_tools(self) -> List[str]:
        """Get available tools for the agent."""
        return [
            "validate_quantity_consistency",
            "validate_weight_consistency",
            "validate_entity_consistency",
            "validate_product_descriptions",
            "validate_value_consistency",
            "validate_geographic_consistency",
            "validate_unit_calculations",
            "validate_weight_ratios",
            "validate_package_calculations",
            "detect_round_number_patterns",
            "detect_product_substitution",
            "detect_origin_manipulation",
            "detect_entity_variations",
            "synthesize_fraud_evidence"
        ]

    def suggest_initial_strategy(self, extracted_content: Dict[str, str], document_types: Dict[str, str]) -> str:
        """Suggest initial investigation strategy."""

        doc_type_list = list(document_types.values())

        if "commercial_invoice" in doc_type_list and "packing_list" in doc_type_list:
            return "Start with quantity and weight consistency validation"
        elif "commercial_invoice" in doc_type_list:
            return "Focus on value and calculation validation"
        else:
            return "Begin with available document analysis"


class Thinker:
    """Generates reasoning about next actions."""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.logger = workflow_logger.logger

    def think(self, observation: Observation, history: List[AgentStep]) -> Reasoning:
        """Generate reasoning about next actions using LLM."""

        try:
            prompt = self.build_reasoning_prompt(observation, history)
            llm_response = self.llm.invoke(prompt)

            return self.parse_reasoning(llm_response.content)

        except Exception as e:
            self.logger.error(f"Error in thinking: {str(e)}")
            # Fallback reasoning
            return Reasoning(
                content="Unable to generate reasoning due to error",
                recommended_action="synthesize_fraud_evidence",
                confidence=0.0,
                reasoning_type="fallback"
            )

    def build_reasoning_prompt(self, observation: Observation, history: List[AgentStep]) -> str:
        """Build prompt for reasoning."""

        history_summary = self.format_history(history)

        return f"""
        You are a fraud detection expert analyzing customs documents.
        
        CURRENT INVESTIGATION STATE:
        - Total documents: {observation.total_documents}
        - Document types: {list(observation.document_types.values())}
        - Content summary: {observation.content_summary}
        - Risk indicators: {observation.risk_indicators}
        - Fraud indicators found: {observation.fraud_indicators or []}
        - Evidence collected: {len(observation.evidence_collected or [])} items
        - Tools executed: {observation.tools_executed or []}
        - Confidence level: {observation.confidence_level}
        - Iteration: {observation.iteration_count}
        
        AVAILABLE TOOLS:
        {', '.join(observation.available_tools)}
        
        INVESTIGATION HISTORY:
        {history_summary}
        
        Based on this information, what should I investigate next?
        
        Consider:
        1. What fraud patterns might be present given the document types?
        2. Which tools would be most useful at this stage?
        3. What evidence do I still need to gather?
        4. Am I ready to make a final assessment?
        
        Provide your reasoning and recommend the next action.
        Format your response as:
        REASONING: [your reasoning]
        RECOMMENDED_ACTION: [tool name]
        CONFIDENCE: [0.0 to 1.0]
        REASONING_TYPE: [investigation/validation/synthesis]
        """

    def format_history(self, history: List[AgentStep]) -> str:
        """Format investigation history for prompt."""
        if not history:
            return "Investigation just started."

        history_parts = []
        for step in history[-5:]:  # Last 5 steps
            history_parts.append(f"Step {step.step_number}: {step.step_type}")
            if step.tool_used:
                history_parts.append(f"  Tool: {step.tool_used}")
            history_parts.append(f"  Content: {step.content[:100]}...")
            history_parts.append("")

        return "\n".join(history_parts)

    def parse_reasoning(self, llm_response: str) -> Reasoning:
        """Parse LLM response into Reasoning object."""

        try:
            lines = llm_response.strip().split('\n')
            reasoning_content = ""
            recommended_action = "synthesize_fraud_evidence"  # Default
            confidence = 0.5  # Default
            reasoning_type = "investigation"  # Default

            for line in lines:
                if line.startswith("REASONING:"):
                    reasoning_content = line.replace("REASONING:", "").strip()
                elif line.startswith("RECOMMENDED_ACTION:"):
                    recommended_action = line.replace(
                        "RECOMMENDED_ACTION:", "").strip()
                elif line.startswith("CONFIDENCE:"):
                    try:
                        confidence = float(line.replace(
                            "CONFIDENCE:", "").strip())
                    except ValueError:
                        confidence = 0.5
                elif line.startswith("REASONING_TYPE:"):
                    reasoning_type = line.replace(
                        "REASONING_TYPE:", "").strip()

            # If parsing failed, use the full response as reasoning
            if not reasoning_content:
                reasoning_content = llm_response

            return Reasoning(
                content=reasoning_content,
                recommended_action=recommended_action,
                confidence=confidence,
                reasoning_type=reasoning_type
            )

        except Exception as e:
            self.logger.warning(
                f"Could not parse reasoning response: {str(e)}")
            return Reasoning(
                content=llm_response,
                recommended_action="synthesize_fraud_evidence",
                confidence=0.5,
                reasoning_type="investigation"
            )


class Actor:
    """Executes actions based on reasoning."""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.logger = workflow_logger.logger
        self.tools = {tool.name: tool for tool in get_all_tools()}

    def act(self, reasoning: Reasoning, extracted_content: Dict[str, str]) -> Action:
        """Execute actions based on reasoning."""

        try:
            # Get the recommended tool
            tool_name = reasoning.recommended_action

            if tool_name not in self.tools:
                self.logger.warning(
                    f"Tool {tool_name} not found, using synthesize_fraud_evidence")
                tool_name = "synthesize_fraud_evidence"

            tool = self.tools[tool_name]

            # Execute the tool
            result = self.execute_tool(tool, extracted_content)

            return Action(
                tool_name=tool_name,
                reasoning=reasoning,
                result=result,
                timestamp=datetime.utcnow()
            )

        except Exception as e:
            self.logger.error(f"Error in action execution: {str(e)}")
            return Action(
                tool_name="error",
                reasoning=reasoning,
                result=f"Action failed: {str(e)}",
                timestamp=datetime.utcnow()
            )

    def execute_tool(self, tool, extracted_content: Dict[str, str]) -> str:
        """Execute a specific tool."""

        try:
            # Classify documents properly
            document_types = {}
            for filename, content in extracted_content.items():
                doc_type = self.classify_document_type(filename, content)
                document_types[filename] = doc_type

            # Convert extracted content to bundle format for tools
            bundle_data = {
                "bundle_id": f"bundle_{uuid.uuid4().hex[:8]}",
                "documents": [
                    {
                        # Default to commercial_invoice
                        "document_type": document_types.get(filename, "commercial_invoice"),
                        "filename": filename,
                        "content": content
                    }
                    for filename, content in extracted_content.items()
                ]
            }

            # Execute the tool
            result = tool._run(bundle_data=bundle_data)
            return result

        except Exception as e:
            self.logger.error(f"Tool execution failed: {str(e)}")
            return f"Tool execution failed: {str(e)}"

    def classify_document_type(self, filename: str, content: str) -> str:
        """Classify document type based on filename and content."""

        # Simple classification based on filename
        filename_lower = filename.lower()

        if "invoice" in filename_lower:
            return "commercial_invoice"
        elif "packing" in filename_lower or "pack" in filename_lower:
            return "packing_list"
        elif "bill" in filename_lower and "lading" in filename_lower:
            return "bill_of_lading"
        elif "origin" in filename_lower or "certificate" in filename_lower:
            return "certificate_of_origin"
        elif "customs" in filename_lower or "declaration" in filename_lower:
            return "customs_declaration"
        else:
            # Try to classify based on content
            content_lower = content.lower()
            if "invoice" in content_lower or "bill" in content_lower:
                return "commercial_invoice"
            elif "packing" in content_lower or "pack" in content_lower:
                return "packing_list"
            elif "lading" in content_lower:
                return "bill_of_lading"
            elif "origin" in content_lower:
                return "certificate_of_origin"
            elif "customs" in content_lower:
                return "customs_declaration"
            else:
                # Default to commercial_invoice if we can't determine
                return "commercial_invoice"


class ReActFraudDetectionAgent:
    """True ReAct fraud detection agent."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )

        self.observer = Observer(self.llm)
        self.thinker = Thinker(self.llm)
        self.actor = Actor(self.llm)
        self.logger = workflow_logger.logger

        # Configuration
        self.max_iterations = settings.max_iterations
        self.confidence_threshold = settings.confidence_threshold

    def analyze_documents(self, extracted_content: Dict[str, str], options: Optional[Dict[str, Any]] = None) -> AgentExecution:
        """Main ReAct loop for fraud detection."""

        execution_id = str(uuid.uuid4())
        options = options or {}

        # Initialize memory
        memory = FraudDetectionMemory(
            execution_id, f"bundle_{uuid.uuid4().hex[:8]}")
        memory.initialize_investigation(extracted_content)

        try:
            self.logger.info(
                f"Starting ReAct fraud analysis with {len(extracted_content)} documents")

            # ReAct Loop
            iteration = 0
            while iteration < self.max_iterations:
                iteration += 1
                memory.set_iteration_count(iteration)

                # OBSERVE
                observation = self.observer.observe(extracted_content, memory)
                memory.add_observation(
                    f"Observation {iteration}: {observation.content_summary}")

                # THINK
                reasoning = self.thinker.think(
                    observation, memory.get_agent_execution().steps)
                memory.add_thought(reasoning.content)

                # ACT
                action = self.actor.act(reasoning, extracted_content)
                memory.add_action(
                    f"Executed {action.tool_name}",
                    action.tool_name,
                    {"reasoning": reasoning.content},
                    action.result
                )

                # Update confidence
                memory.update_confidence(reasoning.confidence)

                # Check termination conditions
                if self.should_terminate(memory, observation, reasoning):
                    self.logger.info(
                        f"ReAct loop terminating after {iteration} iterations")
                    break

            # Generate final assessment
            final_assessment = self.generate_final_assessment(
                memory, extracted_content)
            memory.agent_execution.complete_execution(final_assessment)

            self.logger.info(f"ReAct analysis completed: {execution_id}")
            return memory.get_agent_execution()

        except Exception as e:
            self.logger.error(f"Error in ReAct analysis: {str(e)}")
            memory.agent_execution.fail_execution(str(e))
            return memory.get_agent_execution()

    def should_terminate(self, memory: FraudDetectionMemory, observation: Observation, reasoning: Reasoning) -> bool:
        """Determine if the ReAct loop should terminate."""

        # High confidence and synthesis reasoning
        if (reasoning.confidence >= self.confidence_threshold and
                reasoning.reasoning_type == "synthesis"):
            return True

        # Maximum iterations reached
        if memory.get_iteration_count() >= self.max_iterations:
            return True

        # No new findings in recent iterations
        if memory.get_iteration_count() > 5 and reasoning.confidence < 0.3:
            return True

        return False

    def generate_final_assessment(self, memory: FraudDetectionMemory, extracted_content: Dict[str, str]) -> FraudAnalysisResult:
        """Generate final fraud assessment."""

        try:
            # Use synthesis tool for final assessment
            synthesis_tool = self.actor.tools.get("synthesize_fraud_evidence")
            if synthesis_tool:
                # Classify documents properly
                document_types = {}
                for filename, content in extracted_content.items():
                    doc_type = self.actor.classify_document_type(
                        filename, content)
                    document_types[filename] = doc_type

                bundle_data = {
                    "bundle_id": f"bundle_{uuid.uuid4().hex[:8]}",
                    "documents": [
                        {
                            "document_type": document_types.get(filename, "commercial_invoice"),
                            "filename": filename,
                            "content": content
                        }
                        for filename, content in extracted_content.items()
                    ]
                }

                analysis_results = memory.get_analysis_results()
                result = synthesis_tool._run(
                    bundle_data=bundle_data,
                    options={"analysis_results": analysis_results}
                )
            else:
                result = "Synthesis tool not available"

            # Create structured result
            return self.create_fraud_analysis_result(memory, result)

        except Exception as e:
            self.logger.error(f"Error in final assessment: {str(e)}")
            return self.create_fallback_analysis(memory, str(e))

    def create_fraud_analysis_result(self, memory: FraudDetectionMemory, synthesis_result: str) -> FraudAnalysisResult:
        """Create structured fraud analysis result."""

        # Basic fraud detection based on keywords
        fraud_keywords = ["fraud detected", "suspicious",
                          "inconsistency", "discrepancy", "manipulation"]
        fraud_detected = any(keyword.lower() in synthesis_result.lower()
                             for keyword in fraud_keywords)

        # Calculate confidence
        confidence = memory.get_confidence_level()

        # Determine risk level
        if confidence >= 0.8:
            risk_level = "CRITICAL"
        elif confidence >= 0.6:
            risk_level = "HIGH"
        elif confidence >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return FraudAnalysisResult(
            bundle_id=memory.bundle_id,
            analysis_id=str(uuid.uuid4()),
            fraud_detected=fraud_detected,
            overall_confidence=confidence,
            risk_level=risk_level,
            fraud_indicators=memory.get_fraud_indicators(),
            evidence=memory.get_evidence(),
            recommended_actions=["Review findings",
                                 "Conduct manual verification"],
            investigation_priority="MEDIUM",
            executive_summary=synthesis_result,
            technical_details={"synthesis_result": synthesis_result}
        )

    def create_fallback_analysis(self, memory: FraudDetectionMemory, error: str) -> FraudAnalysisResult:
        """Create fallback analysis when synthesis fails."""

        return FraudAnalysisResult(
            bundle_id=memory.bundle_id,
            analysis_id=str(uuid.uuid4()),
            fraud_detected=False,
            overall_confidence=0.0,
            risk_level="LOW",
            fraud_indicators=[],
            evidence=[],
            recommended_actions=[
                "Manual review required due to analysis error"],
            investigation_priority="LOW",
            executive_summary=f"Analysis incomplete due to error: {error}",
            technical_details={"error": error}
        )

    async def analyze_documents_stream(
        self,
        extracted_content: Dict[str, str],
        options: Optional[Dict[str, Any]] = None,
        stream_queue: Optional[asyncio.Queue] = None
    ) -> AgentExecution:
        """Streaming version of ReAct fraud detection analysis."""

        execution_id = str(uuid.uuid4())
        options = options or {}

        # Initialize memory
        memory = FraudDetectionMemory(
            execution_id, f"bundle_{uuid.uuid4().hex[:8]}")
        memory.initialize_investigation(extracted_content)

        try:
            self.logger.info(
                f"Starting streaming ReAct fraud analysis with {len(extracted_content)} documents")

            # Send initial streaming update
            if stream_queue:
                await stream_queue.put({
                    "type": "analysis_started",
                    "message": f"Starting ReAct fraud analysis with {len(extracted_content)} documents",
                    "execution_id": execution_id,
                    "timestamp": datetime.utcnow().isoformat()
                })

            # ReAct Loop with streaming updates
            iteration = 0
            while iteration < self.max_iterations:
                iteration += 1
                memory.set_iteration_count(iteration)

                # Send iteration start update
                if stream_queue:
                    await stream_queue.put({
                        "type": "iteration_started",
                        "iteration": iteration,
                        "message": f"Starting iteration {iteration}",
                        "timestamp": datetime.utcnow().isoformat()
                    })

                # OBSERVE
                observation = self.observer.observe(extracted_content, memory)
                memory.add_observation(
                    f"Observation {iteration}: {observation.content_summary}")

                # Send observation update
                if stream_queue:
                    await stream_queue.put({
                        "type": "observation_completed",
                        "iteration": iteration,
                        "observation": observation.content_summary,
                        "message": f"Observation {iteration} completed",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    # Small delay to ensure updates are sent immediately
                    await asyncio.sleep(0.1)

                # THINK
                reasoning = self.thinker.think(
                    observation, memory.get_agent_execution().steps)
                memory.add_thought(reasoning.content)

                # Send reasoning update
                if stream_queue:
                    await stream_queue.put({
                        "type": "reasoning_completed",
                        "iteration": iteration,
                        "reasoning": reasoning.content,
                        "confidence": reasoning.confidence,
                        "recommended_action": reasoning.recommended_action,
                        "message": f"Reasoning {iteration} completed",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    # Small delay to ensure updates are sent immediately
                    await asyncio.sleep(0.1)

                # ACT
                action = self.actor.act(reasoning, extracted_content)
                memory.add_action(
                    f"Executed {action.tool_name}",
                    action.tool_name,
                    {"reasoning": reasoning.content},
                    action.result
                )

                # Send action update
                if stream_queue:
                    await stream_queue.put({
                        "type": "action_completed",
                        "iteration": iteration,
                        "tool_used": action.tool_name,
                        "action_result": action.result[:200] + "..." if len(action.result) > 200 else action.result,
                        "message": f"Action {iteration} completed using {action.tool_name}",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    # Small delay to ensure updates are sent immediately
                    await asyncio.sleep(0.1)

                # Update confidence
                memory.update_confidence(reasoning.confidence)

                # Check termination conditions
                if self.should_terminate(memory, observation, reasoning):
                    self.logger.info(
                        f"ReAct loop terminating after {iteration} iterations")

                    if stream_queue:
                        await stream_queue.put({
                            "type": "termination_condition_met",
                            "iteration": iteration,
                            "confidence": reasoning.confidence,
                            "reasoning_type": reasoning.reasoning_type,
                            "message": f"Termination condition met after {iteration} iterations",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    break

            # Generate final assessment
            final_assessment = self.generate_final_assessment(
                memory, extracted_content)
            memory.agent_execution.complete_execution(final_assessment)

            # Send completion update
            if stream_queue:
                await stream_queue.put({
                    "type": "analysis_completed",
                    "execution_id": execution_id,
                    "total_iterations": iteration,
                    "final_confidence": memory.get_confidence_level(),
                    "fraud_detected": final_assessment.fraud_detected,
                    "risk_level": final_assessment.risk_level,
                    "message": f"ReAct analysis completed in {iteration} iterations",
                    "timestamp": datetime.utcnow().isoformat()
                })

            self.logger.info(
                f"Streaming ReAct analysis completed: {execution_id}")
            return memory.get_agent_execution()

        except Exception as e:
            self.logger.error(f"Error in streaming ReAct analysis: {str(e)}")

            # Send error update
            if stream_queue:
                await stream_queue.put({
                    "type": "analysis_error",
                    "error": str(e),
                    "message": f"ReAct analysis failed: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                })

            memory.agent_execution.fail_execution(str(e))
            return memory.get_agent_execution()
