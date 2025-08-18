"""Logging configuration for the fraud detection agent."""

import sys
import os
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from loguru import logger

from ..config import settings


class StreamingLogger:
    """Logger that can stream updates to UI in real-time."""

    def __init__(self):
        self.stream_callbacks: List[Callable] = []
        self.bundle_id: Optional[str] = None

    def set_bundle_id(self, bundle_id: str):
        """Set the current bundle ID for streaming updates."""
        self.bundle_id = bundle_id

    def add_stream_callback(self, callback: Callable):
        """Add a callback function to receive streaming updates."""
        self.stream_callbacks.append(callback)

    def remove_stream_callback(self, callback: Callable):
        """Remove a callback function."""
        if callback in self.stream_callbacks:
            self.stream_callbacks.remove(callback)

    async def stream_update(self, update_type: str, **kwargs):
        """Send a streaming update to all registered callbacks."""
        update = {
            "type": update_type,
            "timestamp": asyncio.get_event_loop().time(),
            "bundle_id": self.bundle_id,
            **kwargs
        }

        for callback in self.stream_callbacks:
            try:
                await callback(update)
            except Exception as e:
                # Log error but don't break other callbacks
                logger.error(f"Stream callback error: {e}")


# Global streaming logger instance
streaming_logger = StreamingLogger()


class WorkflowLogger:
    """Custom logger for workflow monitoring with structured human-readable output."""

    def __init__(self):
        self.logger = logger
        self._setup_logging()

    def _setup_logging(self):
        """Configure loguru with custom formatting and handlers."""
        # Remove default handler
        logger.remove()

        # Get log level from settings
        log_level = settings.log_level.upper()

        # Console handler with custom format
        logger.add(
            sys.stdout,
            format=self._get_console_format(),
            level=log_level,
            colorize=True,
            backtrace=True,
            diagnose=True
        )

        # File handler for detailed logs
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Clear the log file on startup
        log_file = log_dir / "app.log"
        if log_file.exists():
            log_file.unlink()  # Delete the existing log file

        logger.add(
            log_file,
            format=self._get_file_format(),
            level="DEBUG",
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )

    def _get_console_format(self) -> str:
        """Get console log format with emojis and structured data."""
        return (
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <5}</level>| "
            "<cyan>{extra[caller_short]}</cyan> | "
            "<level>{message}</level>"
        )

    def _get_file_format(self) -> str:
        """Get file log format with more detailed information."""
        return (
            "{time:HH:mm:ss.SSS} | "
            "{level: <5} | "
            "{extra[caller_short]} | "
            "{message} | "
            "extra={extra}"
        )

    def log_workflow_step(self, step: str, **kwargs):
        """Log a workflow step with structured data."""
        import inspect

        # Get caller information - go up the call stack to find the actual application caller
        caller_frame = inspect.currentframe().f_back
        while caller_frame:
            caller_info = inspect.getframeinfo(caller_frame)
            filename = caller_info.filename.split('/')[-1]
            # Skip our own logging functions
            if filename not in ['logging_config.py'] and not filename.startswith('loguru'):
                caller_location = f"{caller_info.filename.split('/')[-1]}:{caller_info.function}:{caller_info.lineno}"
                caller_short = f"{filename}:{caller_info.lineno}"
                break
            caller_frame = caller_frame.f_back
        else:
            caller_location = "unknown:unknown:0"
            caller_short = "unknown:0"

        emoji_map = {
            "upload": "📄",
            "preprocess": "🔍",
            "llm": "🤖",
            "agent": "🧠",
            "tool": "🔧",
            "validation": "✅",
            "error": "❌",
            "warning": "⚠️",
            "result": "🎯",
            "start": "🚀",
            "complete": "✅",
            "extract": "📋",
            "analyze": "🔬",
            "detect": "🕵️",
            "validate": "✓",
            "cross_validate": "🔄"
        }

        emoji = emoji_map.get(step.lower(), "📝")
        message = f"{emoji} {step.title()}"

        if kwargs:
            # Format structured data in a readable way
            data_parts = []
            for key, value in kwargs.items():
                if isinstance(value, (dict, list)):
                    data_parts.append(f"{key}={str(value)[:100]}...")
                else:
                    data_parts.append(f"{key}={value}")

            if data_parts:
                message += f" | {' | '.join(data_parts)}"

        # Add caller information to extra data
        extra_data = {"caller": caller_location, "caller_short": caller_short}
        self.logger.bind(**extra_data).info(message)

    async def log_workflow_step_stream(self, step: str, **kwargs):
        """Log a workflow step and stream it to UI."""
        # Log normally
        self.log_workflow_step(step, **kwargs)

        # Stream to UI
        await streaming_logger.stream_update("preprocessing_step", step=step, **kwargs)

    def log_llm_request(self, model: str, prompt_length: int, **kwargs):
        """Log LLM request details."""
        self.log_workflow_step(
            "llm_request",
            model=model,
            prompt_length=f"{prompt_length:,} chars",
            **kwargs
        )

    def log_llm_response(self, model: str, tokens_used: int, response_time: float, **kwargs):
        """Log LLM response details."""
        self.log_workflow_step(
            "llm_response",
            model=model,
            tokens_used=tokens_used,
            response_time=f"{response_time:.2f}s",
            **kwargs
        )

    def log_agent_action(self, tool_name: str, input_data: Dict[str, Any], result: str, **kwargs):
        """Log agent tool usage."""
        self.log_workflow_step(
            "agent_action",
            tool=tool_name,
            input=str(input_data)[
                :100] + "..." if len(str(input_data)) > 100 else str(input_data),
            result=result[:100] + "..." if len(result) > 100 else result,
            **kwargs
        )

    def log_document_processing(self, doc_type: str, file_size: str, pages: int, **kwargs):
        """Log document processing details."""
        self.log_workflow_step(
            "document_processing",
            type=doc_type,
            size=file_size,
            pages=pages,
            **kwargs
        )

    def log_fraud_detection(self, confidence: float, indicators: list, **kwargs):
        """Log fraud detection results."""
        self.log_workflow_step(
            "fraud_detection",
            confidence=f"{confidence:.1%}",
            indicators=len(indicators),
            **kwargs
        )

    def log_error(self, error_type: str, error_message: str, **kwargs):
        """Log errors with context."""
        self.log_workflow_step(
            "error",
            type=error_type,
            message=error_message,
            **kwargs
        )

    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics."""
        self.log_workflow_step(
            "performance",
            operation=operation,
            duration=f"{duration:.3f}s",
            **kwargs
        )


# Global logger instance
workflow_logger = WorkflowLogger()


# Convenience functions for easy access
def log_step(step: str, **kwargs):
    """Log a workflow step."""
    workflow_logger.log_workflow_step(step, **kwargs)


async def log_step_stream(step: str, **kwargs):
    """Log a workflow step and stream it to UI."""
    await workflow_logger.log_workflow_step_stream(step, **kwargs)


def log_llm(model: str, prompt_length: int, **kwargs):
    """Log LLM request."""
    workflow_logger.log_llm_request(model, prompt_length, **kwargs)


def log_agent(tool: str, input_data: Dict[str, Any], result: str, **kwargs):
    """Log agent action."""
    workflow_logger.log_agent_action(tool, input_data, result, **kwargs)


def log_document(doc_type: str, file_size: str, pages: int, **kwargs):
    """Log document processing."""
    workflow_logger.log_document_processing(
        doc_type, file_size, pages, **kwargs)


def log_fraud(confidence: float, indicators: list, **kwargs):
    """Log fraud detection."""
    workflow_logger.log_fraud_detection(confidence, indicators, **kwargs)


def log_error(error_type: str, error_message: str, **kwargs):
    """Log error."""
    workflow_logger.log_error(error_type, error_message, **kwargs)


def log_performance(operation: str, duration: float, **kwargs):
    """Log performance."""
    workflow_logger.log_performance(operation, duration, **kwargs)


def log_llm_call(model: str, prompt: str, response: str, duration: float, **kwargs):
    """Log a complete LLM call with request and response."""
    prompt_length = len(prompt)
    response_length = len(response)

    workflow_logger.log_workflow_step(
        "llm_call",
        model=model,
        prompt_length=f"{prompt_length:,} chars",
        response_length=f"{response_length:,} chars",
        duration=f"{duration:.3f}s",
        **kwargs
    )


async def log_llm_call_stream(model: str, prompt: str, response: str, duration: float, **kwargs):
    """Log a complete LLM call and stream it to UI."""
    prompt_length = len(prompt)
    response_length = len(response)

    await workflow_logger.log_workflow_step_stream(
        "llm_call",
        model=model,
        prompt_length=f"{prompt_length:,} chars",
        response_length=f"{response_length:,} chars",
        duration=f"{duration:.3f}s",
        **kwargs
    )


# Streaming-specific convenience functions
async def log_preprocessing_step(step: str, filename: str = None, **kwargs):
    """Log a preprocessing step and stream it to UI."""
    await streaming_logger.stream_update(
        "preprocessing_step",
        step=step,
        filename=filename,
        **kwargs
    )


async def log_vision_processing(filename: str, page: int = None, total_pages: int = None, **kwargs):
    """Log vision processing step and stream it to UI."""
    await streaming_logger.stream_update(
        "vision_processing",
        filename=filename,
        page=page,
        total_pages=total_pages,
        **kwargs
    )


async def log_document_extraction(filename: str, document_type: str, **kwargs):
    """Log document extraction step and stream it to UI."""
    await streaming_logger.stream_update(
        "document_extraction",
        filename=filename,
        document_type=document_type,
        **kwargs
    )


def set_streaming_bundle_id(bundle_id: str):
    """Set the bundle ID for streaming updates."""
    streaming_logger.set_bundle_id(bundle_id)


def add_streaming_callback(callback: Callable):
    """Add a callback for streaming updates."""
    streaming_logger.add_stream_callback(callback)


def remove_streaming_callback(callback: Callable):
    """Remove a callback for streaming updates."""
    streaming_logger.remove_stream_callback(callback)


class LLMLoggingWrapper:
    """Wrapper for LLM calls to add logging."""

    def __init__(self, llm_instance, model_name: str):
        self.llm = llm_instance
        self.model_name = model_name

    def invoke(self, prompt: str, **kwargs):
        """Invoke LLM with logging."""
        import time
        start_time = time.time()

        # Log the request
        log_llm(self.model_name, len(prompt),
                prompt=prompt,
                **kwargs)

        try:
            # Make the actual LLM call
            response = self.llm.invoke(prompt, **kwargs)

            # Calculate duration
            duration = time.time() - start_time

            # Log the response
            log_llm_call(
                self.model_name,
                prompt,
                response.content,
                duration,
                response=response.content
            )

            return response

        except Exception as e:
            duration = time.time() - start_time
            log_error("llm_call_error", str(e), model=self.model_name,
                      duration=f"{duration:.3f}s")
            raise
