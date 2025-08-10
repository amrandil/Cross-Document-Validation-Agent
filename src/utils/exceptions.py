"""Custom exceptions for the fraud detection agent."""

from typing import Optional, Dict, Any


class FraudDetectionError(Exception):
    """Base exception for fraud detection errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class DocumentProcessingError(FraudDetectionError):
    """Exception raised when document processing fails."""

    def __init__(
        self,
        message: str,
        document_type: Optional[str] = None,
        filename: Optional[str] = None,
        **kwargs
    ):
        self.document_type = document_type
        self.filename = filename
        details = kwargs.get('details', {})
        if document_type:
            details['document_type'] = document_type
        if filename:
            details['filename'] = filename
        super().__init__(message, error_code="DOCUMENT_PROCESSING_ERROR", details=details)


class ValidationError(FraudDetectionError):
    """Exception raised when validation fails."""

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        validation_type: Optional[str] = None,
        **kwargs
    ):
        self.field_name = field_name
        self.validation_type = validation_type
        details = kwargs.get('details', {})
        if field_name:
            details['field_name'] = field_name
        if validation_type:
            details['validation_type'] = validation_type
        super().__init__(message, error_code="VALIDATION_ERROR", details=details)


class AgentExecutionError(FraudDetectionError):
    """Exception raised when agent execution fails."""

    def __init__(
        self,
        message: str,
        execution_id: Optional[str] = None,
        step_number: Optional[int] = None,
        tool_name: Optional[str] = None,
        **kwargs
    ):
        self.execution_id = execution_id
        self.step_number = step_number
        self.tool_name = tool_name
        details = kwargs.get('details', {})
        if execution_id:
            details['execution_id'] = execution_id
        if step_number:
            details['step_number'] = step_number
        if tool_name:
            details['tool_name'] = tool_name
        super().__init__(message, error_code="AGENT_EXECUTION_ERROR", details=details)


class ConfigurationError(FraudDetectionError):
    """Exception raised when configuration is invalid."""

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        self.config_key = config_key
        details = kwargs.get('details', {})
        if config_key:
            details['config_key'] = config_key
        super().__init__(message, error_code="CONFIGURATION_ERROR", details=details)


class ExternalServiceError(FraudDetectionError):
    """Exception raised when external service calls fail."""

    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs
    ):
        self.service_name = service_name
        self.status_code = status_code
        details = kwargs.get('details', {})
        if service_name:
            details['service_name'] = service_name
        if status_code:
            details['status_code'] = status_code
        super().__init__(message, error_code="EXTERNAL_SERVICE_ERROR", details=details)
