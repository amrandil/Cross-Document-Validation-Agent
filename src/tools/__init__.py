"""Fraud detection tools for the ReAct agent."""

from .document_extraction import DocumentExtractionTool
from .cross_document_validation import (
    QuantityConsistencyTool,
    WeightConsistencyTool,
    EntityConsistencyTool,
    ProductDescriptionTool,
    ValueConsistencyTool,
    GeographicConsistencyTool,
    TimingAnomalyTool
)
from .mathematical_validation import (
    UnitCalculationTool,
    WeightRatioTool,
    PackageCalculationTool,
    RoundNumberPatternTool
)
from .pattern_detection import (
    ProductSubstitutionTool,
    OriginManipulationTool,
    EntityVariationTool,
    FraudEvidenceSynthesisTool
)


def get_all_tools():
    """Get all available fraud detection tools."""
    return [
        # Document processing
        DocumentExtractionTool(),

        # Cross-document validation (only fixed tools for now)
        QuantityConsistencyTool(),
        WeightConsistencyTool(),

        # TODO: Fix remaining tools and add them back:
        # EntityConsistencyTool(),
        # ProductDescriptionTool(),
        # ValueConsistencyTool(),
        # GeographicConsistencyTool(),
        # TimingAnomalyTool(),
        # UnitCalculationTool(),
        # WeightRatioTool(),
        # PackageCalculationTool(),
        # RoundNumberPatternTool(),
        # ProductSubstitutionTool(),
        # OriginManipulationTool(),
        # EntityVariationTool(),
        # FraudEvidenceSynthesisTool()
    ]


__all__ = [
    "get_all_tools",
    "DocumentExtractionTool",
    "QuantityConsistencyTool",
    "WeightConsistencyTool",
    "EntityConsistencyTool",
    "ProductDescriptionTool",
    "ValueConsistencyTool",
    "GeographicConsistencyTool",
    "TimingAnomalyTool",
    "UnitCalculationTool",
    "WeightRatioTool",
    "PackageCalculationTool",
    "RoundNumberPatternTool",
    "ProductSubstitutionTool",
    "OriginManipulationTool",
    "EntityVariationTool",
    "FraudEvidenceSynthesisTool"
]
