"""Base tool class for fraud detection tools."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from ..models.documents import DocumentBundle


class FraudDetectionToolInput(BaseModel):
    """Base input schema for fraud detection tools."""
    bundle_data: Dict[str,
                      Any] = Field(..., description="Document bundle data")
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Tool-specific options")


class BaseFraudDetectionTool(BaseTool, ABC):
    """Base class for all fraud detection tools."""

    args_schema: type[BaseModel] = FraudDetectionToolInput

    def __init__(self, **kwargs):
        # Set name and description if not already set
        if 'name' not in kwargs and hasattr(self, '_name'):
            kwargs['name'] = self._name
        if 'description' not in kwargs and hasattr(self, '_description'):
            kwargs['description'] = self._description

        super().__init__(**kwargs)

    def _run(self, bundle_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> str:
        """Execute the tool with the given bundle data."""
        try:
            options = options or {}

            # Parse bundle data if needed
            bundle = self._parse_bundle_data(bundle_data)

            # Execute the specific tool logic
            result = self._execute(bundle, options)

            return result

        except Exception as e:
            return f"Error executing {self.name}: {str(e)}"

    def _parse_bundle_data(self, bundle_data: Dict[str, Any]) -> DocumentBundle:
        """Parse bundle data into DocumentBundle object."""
        try:
            # Handle both dict and DocumentBundle inputs
            if isinstance(bundle_data, dict):
                return DocumentBundle(**bundle_data)
            elif isinstance(bundle_data, DocumentBundle):
                return bundle_data
            else:
                raise ValueError(
                    f"Invalid bundle data type: {type(bundle_data)}")
        except Exception as e:
            raise

    @abstractmethod
    def _execute(self, bundle: DocumentBundle, options: Dict[str, Any]) -> str:
        """Execute the specific tool logic. Must be implemented by subclasses."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass
