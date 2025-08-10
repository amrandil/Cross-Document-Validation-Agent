"""Mathematical validation tools for fraud detection."""

import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI

from .base import BaseFraudDetectionTool
from ..models.documents import DocumentBundle
from ..config import settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


class UnitCalculationTool(BaseFraudDetectionTool):
    """Tool to validate unit price calculations."""

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )

    @property
    def name(self) -> str:
        return "validate_unit_calculations"

    @property
    def description(self) -> str:
        return """Validate that unit price calculations are mathematically correct (quantity × unit price = total value).
        This tool identifies calculation errors that may indicate deliberate manipulation."""

    def _execute(self, bundle: DocumentBundle, options: Dict[str, Any]) -> str:
        """Validate unit price calculations."""
        try:
            extracted_data = options.get('extracted_data', {})

            prompt = f"""
            Verify the mathematical accuracy of unit price calculations in these customs documents.
            
            Document Data:
            {json.dumps(extracted_data, indent=2, default=str)}
            
            Instructions:
            1. For each item, verify that: quantity × unit_price = total_value
            2. Check that individual item totals sum to document totals
            3. Identify any mathematical inconsistencies
            4. Assess if calculation errors appear deliberate or accidental
            5. Look for patterns of systematic under-calculation
            
            Analysis should include:
            - Mathematical consistency status (PASS/FAIL)
            - Specific calculation errors found
            - Impact of errors on total declared value
            - Assessment of whether errors appear intentional
            - Fraud confidence based on calculation patterns
            
            Provide detailed calculation verification for customs review.
            """

            response = self.llm.invoke(prompt)
            return f"UNIT CALCULATION ANALYSIS:\n{response.content}"

        except Exception as e:
            return f"Error in unit calculation validation: {str(e)}"


class WeightRatioTool(BaseFraudDetectionTool):
    """Tool to validate weight-to-quantity ratios."""

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )

    @property
    def name(self) -> str:
        return "validate_weight_ratios"

    @property
    def description(self) -> str:
        return """Validate that weight-to-quantity ratios are reasonable for the declared products.
        This tool identifies anomalous weight ratios that may indicate product substitution."""

    def _execute(self, bundle: DocumentBundle, options: Dict[str, Any]) -> str:
        """Validate weight ratios."""
        try:
            extracted_data = options.get('extracted_data', {})

            prompt = f"""
            Analyze weight-to-quantity ratios to identify potential product substitution or misdeclaration.
            
            Document Data:
            {json.dumps(extracted_data, indent=2, default=str)}
            
            Instructions:
            1. Calculate weight per unit for each product
            2. Assess if weight ratios are reasonable for the declared product types
            3. Compare weight ratios across similar products
            4. Identify any unusually heavy or light products
            5. Look for patterns suggesting product substitution
            
            Analysis should cover:
            - Weight ratio consistency (PASS/FAIL)
            - Per-unit weight calculations
            - Reasonableness assessment for product types
            - Identification of anomalous weight ratios
            - Product substitution indicators
            - Confidence in weight-based fraud detection
            
            Focus on detecting products that don't match their declared weight profiles.
            """

            response = self.llm.invoke(prompt)
            return f"WEIGHT RATIO ANALYSIS:\n{response.content}"

        except Exception as e:
            return f"Error in weight ratio validation: {str(e)}"


class PackageCalculationTool(BaseFraudDetectionTool):
    """Tool to validate package count calculations."""

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )

    @property
    def name(self) -> str:
        return "validate_package_calculations"

    @property
    def description(self) -> str:
        return """Validate that package counts align with quantities and are consistent across documents.
        This tool identifies package count discrepancies that may indicate quantity manipulation."""

    def _execute(self, bundle: DocumentBundle, options: Dict[str, Any]) -> str:
        """Validate package calculations."""
        try:
            extracted_data = options.get('extracted_data', {})

            prompt = f"""
            Analyze package counts and their relationship to product quantities across documents.
            
            Document Data:
            {json.dumps(extracted_data, indent=2, default=str)}
            
            Instructions:
            1. Compare package counts between packing list and bill of lading
            2. Assess if package counts are reasonable for the declared quantities
            3. Check for consistency in package descriptions
            4. Identify any package count discrepancies
            5. Look for signs of quantity manipulation through package miscounting
            
            Analysis should include:
            - Package count consistency (PASS/FAIL)
            - Cross-document package comparisons
            - Quantity-to-package ratio assessment
            - Package description consistency
            - Quantity manipulation indicators
            - Package-based fraud confidence
            
            Provide findings for quantity verification purposes.
            """

            response = self.llm.invoke(prompt)
            return f"PACKAGE CALCULATION ANALYSIS:\n{response.content}"

        except Exception as e:
            return f"Error in package calculation validation: {str(e)}"


class RoundNumberPatternTool(BaseFraudDetectionTool):
    """Tool to detect suspiciously round number patterns."""

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )

    @property
    def name(self) -> str:
        return "detect_round_number_patterns"

    @property
    def description(self) -> str:
        return """Detect suspiciously round numbers that may indicate estimated rather than actual values.
        This tool identifies pricing patterns that suggest deliberate undervaluation."""

    def _execute(self, bundle: DocumentBundle, options: Dict[str, Any]) -> str:
        """Detect round number patterns."""
        try:
            extracted_data = options.get('extracted_data', {})

            prompt = f"""
            Analyze numerical values in these documents for suspiciously round number patterns.
            
            Document Data:
            {json.dumps(extracted_data, indent=2, default=str)}
            
            Instructions:
            1. Identify values that are unusually round (ending in multiple zeros)
            2. Look for unit prices that appear to be rough estimates
            3. Check if multiple items have identical unit prices
            4. Assess if round numbers appear across different value categories
            5. Determine if round number patterns suggest deliberate manipulation
            
            Analysis should cover:
            - Round number pattern assessment (PASS/FAIL)
            - Identification of suspiciously round values
            - Patterns suggesting estimation vs. actual pricing
            - Multiple identical values analysis
            - Deliberate manipulation indicators
            - Round number fraud confidence
            
            Focus on patterns that suggest deliberate undervaluation through estimated pricing.
            """

            response = self.llm.invoke(prompt)
            return f"ROUND NUMBER PATTERN ANALYSIS:\n{response.content}"

        except Exception as e:
            return f"Error in round number pattern detection: {str(e)}"
