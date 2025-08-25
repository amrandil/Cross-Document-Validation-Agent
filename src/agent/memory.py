"""Memory management for the fraud detection agent."""

from typing import Dict, Any, List, Optional
from langchain.memory import ConversationBufferMemory
from datetime import datetime

from ..models.fraud import AgentExecution, AgentStep
from ..utils.logging_config import workflow_logger

logger = workflow_logger.logger


class FraudDetectionMemory:
    """Memory management for fraud detection investigations."""

    def __init__(self, execution_id: str, bundle_id: str):
        self.execution_id = execution_id
        self.bundle_id = bundle_id

        # LangChain conversation memory
        self.conversation_memory = ConversationBufferMemory(
            memory_key="agent_scratchpad",
            return_messages=True
        )

        # Agent execution tracking
        self.agent_execution = AgentExecution(
            execution_id=execution_id,
            bundle_id=bundle_id
        )

        # Investigation state
        self.extracted_data: Dict[str, Any] = {}
        self.analysis_results: List[str] = []
        self.current_phase = "initial_observation"
        self.investigation_context: Dict[str, Any] = {}

        # ReAct agent specific state
        self.fraud_indicators: List[str] = []
        self.evidence: List[str] = []
        self.executed_tools: List[str] = []
        self.iteration_count: int = 0
        self.confidence_level: float = 0.0
        self.extracted_content: Dict[str, str] = {}

    def initialize_investigation(self, extracted_content: Dict[str, str]):
        """Initialize investigation with extracted content."""
        self.extracted_content = extracted_content
        self.iteration_count = 0
        self.confidence_level = 0.0
        logger.info(
            f"Initialized investigation with {len(extracted_content)} documents")

    def add_step(self, step_type: str, content: str, tool_used: Optional[str] = None,
                 tool_input: Optional[Dict[str, Any]] = None, tool_output: Optional[str] = None) -> AgentStep:
        """Add a step to the agent execution trace."""
        step = self.agent_execution.add_step(
            step_type=step_type,
            content=content,
            tool_used=tool_used,
            tool_input=tool_input,
            tool_output=tool_output
        )

        # Also add to conversation memory for LangChain
        if step_type == "OBSERVATION":
            self.conversation_memory.chat_memory.add_ai_message(
                f"OBSERVATION: {content}")
        elif step_type == "THOUGHT":
            self.conversation_memory.chat_memory.add_ai_message(
                f"THOUGHT: {content}")
        elif step_type == "ACTION":
            self.conversation_memory.chat_memory.add_ai_message(
                f"ACTION: {content}")
            if tool_output:
                self.conversation_memory.chat_memory.add_user_message(
                    f"RESULT: {tool_output}")

        return step

    def add_observation(self, content: str) -> AgentStep:
        """Add an observation step."""
        return self.add_step("OBSERVATION", content)

    def add_thought(self, content: str) -> AgentStep:
        """Add a thought/reasoning step."""
        return self.add_step("THOUGHT", content)

    def add_action(self, content: str, tool_used: str, tool_input: Dict[str, Any], tool_output: str) -> AgentStep:
        """Add an action step with tool usage."""
        # Track executed tools
        if tool_used and tool_used not in self.executed_tools:
            self.executed_tools.append(tool_used)

        # Add analysis result
        if tool_output:
            self.analysis_results.append(tool_output)

        return self.add_step("ACTION", content, tool_used, tool_input, tool_output)

    def update_extracted_data(self, document_type: str, data: Dict[str, Any]):
        """Update extracted data for a document type."""
        self.extracted_data[document_type] = data

    def add_analysis_result(self, analysis: str):
        """Add an analysis result to the collection."""
        self.analysis_results.append(analysis)

    def set_phase(self, phase: str):
        """Set the current investigation phase."""
        self.current_phase = phase
        self.investigation_context["current_phase"] = phase

    def update_context(self, key: str, value: Any):
        """Update investigation context."""
        self.investigation_context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get investigation context value."""
        return self.investigation_context.get(key, default)

    def get_conversation_history(self) -> str:
        """Get formatted conversation history for prompt."""
        messages = self.conversation_memory.chat_memory.messages
        if not messages:
            return "Investigation just started."

        history_parts = []
        # Last 10 messages to avoid overwhelming the context
        for message in messages[-10:]:
            if hasattr(message, 'content'):
                history_parts.append(message.content)

        return "\n".join(history_parts)

    def get_investigation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current investigation state."""
        return {
            "execution_id": self.execution_id,
            "bundle_id": self.bundle_id,
            "current_phase": self.current_phase,
            "total_steps": len(self.agent_execution.steps),
            "extracted_documents": list(self.extracted_data.keys()),
            "analysis_count": len(self.analysis_results),
            "start_time": self.agent_execution.start_time,
            "duration_ms": self._calculate_duration_ms(),
            "context": self.investigation_context
        }

    def _calculate_duration_ms(self) -> int:
        """Calculate current investigation duration in milliseconds."""
        if self.agent_execution.end_time:
            delta = self.agent_execution.end_time - self.agent_execution.start_time
        else:
            delta = datetime.utcnow() - self.agent_execution.start_time
        return int(delta.total_seconds() * 1000)

    def clear_memory(self):
        """Clear conversation memory while preserving execution trace."""
        self.conversation_memory.clear()
        logger.info("Cleared conversation memory")

    def get_agent_execution(self) -> AgentExecution:
        """Get current agent execution object."""
        return self.agent_execution

    # ReAct agent specific methods
    def get_fraud_indicators(self) -> List[str]:
        """Get fraud indicators found during investigation."""
        return self.fraud_indicators.copy()

    def add_fraud_indicator(self, indicator: str):
        """Add a fraud indicator."""
        if indicator not in self.fraud_indicators:
            self.fraud_indicators.append(indicator)
            logger.debug(f"Added fraud indicator: {indicator}")

    def get_evidence(self) -> List[str]:
        """Get evidence collected during investigation."""
        return self.evidence.copy()

    def add_evidence(self, evidence_item: str):
        """Add evidence item."""
        if evidence_item not in self.evidence:
            self.evidence.append(evidence_item)
            logger.debug(f"Added evidence: {evidence_item}")

    def get_executed_tools(self) -> List[str]:
        """Get list of executed tools."""
        return self.executed_tools.copy()

    def get_iteration_count(self) -> int:
        """Get current iteration count."""
        return self.iteration_count

    def set_iteration_count(self, count: int):
        """Set iteration count."""
        self.iteration_count = count

    def get_confidence_level(self) -> float:
        """Get current confidence level."""
        return self.confidence_level

    def update_confidence(self, confidence: float):
        """Update confidence level."""
        self.confidence_level = confidence
        logger.debug(f"Updated confidence level: {confidence}")

    def get_analysis_results(self) -> List[str]:
        """Get all analysis results."""
        return self.analysis_results.copy()

    def get_extracted_content(self) -> Dict[str, str]:
        """Get extracted content from documents."""
        return self.extracted_content.copy()

    def get_current_state(self) -> Dict[str, Any]:
        """Get current investigation state for ReAct agent."""
        return {
            "extracted_content": self.extracted_content,
            "fraud_indicators": self.fraud_indicators,
            "evidence": self.evidence,
            "executed_tools": self.executed_tools,
            "iteration_count": self.iteration_count,
            "confidence_level": self.confidence_level,
            "analysis_results": self.analysis_results
        }
