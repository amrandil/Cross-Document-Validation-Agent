"""Memory management for the fraud detection agent."""

from typing import Dict, Any, List, Optional
from langchain.memory import ConversationBufferMemory
from datetime import datetime

from ..models.fraud import AgentExecution, AgentStep
from ..utils.logging import get_logger

logger = get_logger(__name__)


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

        logger.info(
            f"Initialized memory for execution {execution_id}, bundle {bundle_id}")

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

        logger.debug(f"Added {step_type} step: {content[:100]}...")
        return step

    def add_observation(self, content: str) -> AgentStep:
        """Add an observation step."""
        return self.add_step("OBSERVATION", content)

    def add_thought(self, content: str) -> AgentStep:
        """Add a thought/reasoning step."""
        return self.add_step("THOUGHT", content)

    def add_action(self, content: str, tool_used: str, tool_input: Dict[str, Any], tool_output: str) -> AgentStep:
        """Add an action step with tool usage."""
        return self.add_step("ACTION", content, tool_used, tool_input, tool_output)

    def update_extracted_data(self, document_type: str, data: Dict[str, Any]):
        """Update extracted data for a document type."""
        self.extracted_data[document_type] = data
        logger.debug(f"Updated extracted data for {document_type}")

    def add_analysis_result(self, analysis: str):
        """Add an analysis result to the collection."""
        self.analysis_results.append(analysis)
        logger.debug(f"Added analysis result: {analysis[:100]}...")

    def set_phase(self, phase: str):
        """Set the current investigation phase."""
        self.current_phase = phase
        self.investigation_context["current_phase"] = phase
        logger.info(f"Investigation phase changed to: {phase}")

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
