"""Pattern detection tools for advanced fraud analysis."""

import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI

from .base import BaseFraudDetectionTool
from ..models.documents import DocumentBundle
from ..config import settings


class ProductSubstitutionTool(BaseFraudDetectionTool):
    """Tool to detect product substitution fraud patterns."""

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )

    @property
    def name(self) -> str:
        return "detect_product_substitution"

    @property
    def description(self) -> str:
        return """Detect sophisticated product substitution schemes by analyzing subtle variations in product descriptions,
        weights, and values across documents. This tool identifies cases where premium products are shipped
        but basic products are declared."""

    def _execute(self, bundle: DocumentBundle, options: Dict[str, Any]) -> str:
        """Detect product substitution patterns."""
        try:
            extracted_data = options.get('extracted_data', {})

            prompt = f"""
            Analyze these documents for sophisticated product substitution fraud schemes.
            
            Document Data:
            {json.dumps(extracted_data, indent=2, default=str)}
            
            Instructions:
            1. Compare product descriptions across documents for subtle quality variations
            2. Analyze value-to-weight ratios to detect premium vs. basic product indicators
            3. Look for additional components/accessories mentioned in some documents but not others
            4. Check for brand quality descriptors (premium, deluxe, professional vs. basic, standard)
            5. Assess if declared values align with product quality indicators
            6. Examine packaging details that might reveal actual product quality
            
            Analysis should include:
            - Product substitution detection (DETECTED/NOT DETECTED)
            - Specific quality variations identified
            - Value-weight ratio analysis supporting substitution
            - Evidence of premium features declared in some documents
            - Estimated impact on declared value
            - Product substitution confidence level
            
            Focus on detecting schemes where high-value products are shipped but low-value products are declared.
            """

            response = self.llm.invoke(prompt)
            return f"PRODUCT SUBSTITUTION ANALYSIS:\n{response.content}"

        except Exception as e:
            return f"Error in product substitution detection: {str(e)}"


class OriginManipulationTool(BaseFraudDetectionTool):
    """Tool to detect origin manipulation and transshipment fraud."""

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )

    @property
    def name(self) -> str:
        return "detect_origin_manipulation"

    @property
    def description(self) -> str:
        return """Detect origin manipulation schemes including transshipment fraud, false origin certificates,
        and geographic inconsistencies designed to evade tariffs and trade restrictions."""

    def _execute(self, bundle: DocumentBundle, options: Dict[str, Any]) -> str:
        """Detect origin manipulation patterns."""
        try:
            extracted_data = options.get('extracted_data', {})

            prompt = f"""
            Analyze these documents for origin manipulation and transshipment fraud schemes.
            
            Document Data:
            {json.dumps(extracted_data, indent=2, default=str)}
            
            Instructions:
            1. Compare declared origin countries across all documents
            2. Analyze shipping routes for geographic impossibilities
            3. Check if supplier locations match declared origin countries
            4. Look for intermediate ports that might indicate transshipment
            5. Identify any entity location mismatches suggesting false origin
            6. Assess if origin claims align with manufacturing capabilities
            
            Analysis should cover:
            - Origin manipulation detection (DETECTED/NOT DETECTED)
            - Geographic consistency assessment
            - Shipping route analysis results
            - Entity location verification
            - Transshipment indicators identified
            - False origin certificate indicators
            - Estimated tariff/duty evasion impact
            - Origin manipulation confidence level
            
            Focus on sophisticated schemes designed to evade trade restrictions and tariffs.
            """

            response = self.llm.invoke(prompt)
            return f"ORIGIN MANIPULATION ANALYSIS:\n{response.content}"

        except Exception as e:
            return f"Error in origin manipulation detection: {str(e)}"


class EntityVariationTool(BaseFraudDetectionTool):
    """Tool to detect suspicious entity variations and misrepresentation."""

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )

    @property
    def name(self) -> str:
        return "detect_entity_variations"

    @property
    def description(self) -> str:
        return """Detect suspicious variations in entity names, addresses, and identification across documents
        that may indicate coordinated misrepresentation or shell company schemes."""

    def _execute(self, bundle: DocumentBundle, options: Dict[str, Any]) -> str:
        """Detect entity variation patterns."""
        try:
            extracted_data = options.get('extracted_data', {})

            prompt = f"""
            Analyze entity information across these documents for suspicious variations or misrepresentation.
            
            Document Data:
            {json.dumps(extracted_data, indent=2, default=str)}
            
            Instructions:
            1. Compare entity names across documents for subtle variations
            2. Analyze address consistency and identify any suspicious changes
            3. Check for coordination between entity variations and other fraud indicators
            4. Look for shell company indicators (minimal address details, generic names)
            5. Assess if entity variations support other fraud schemes (origin manipulation, etc.)
            6. Identify patterns suggesting deliberate misrepresentation
            
            Analysis should include:
            - Entity variation detection (DETECTED/NOT DETECTED)
            - Specific name/address variations identified
            - Shell company indicators
            - Coordination with other fraud schemes
            - Geographic misrepresentation assessment
            - Entity misrepresentation confidence level
            
            Focus on variations that appear coordinated with other fraud indicators.
            """

            response = self.llm.invoke(prompt)
            return f"ENTITY VARIATION ANALYSIS:\n{response.content}"

        except Exception as e:
            return f"Error in entity variation detection: {str(e)}"


class FraudEvidenceSynthesisTool(BaseFraudDetectionTool):
    """Tool to synthesize all fraud evidence into a comprehensive assessment."""

    _name = "synthesize_fraud_evidence"
    _description = """Synthesize all fraud detection results into a comprehensive fraud assessment with
        overall confidence scores, risk levels, and detailed recommendations for customs investigators."""

    def __init__(self):
        super().__init__()
        # LLM is created as a property to avoid Pydantic validation issues

    @property
    def llm(self):
        """Get ChatOpenAI instance for this tool."""
        return ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )

    def _execute(self, bundle: DocumentBundle, options: Dict[str, Any]) -> str:
        """Synthesize all fraud evidence."""
        try:
            # Get all previous analysis results
            analysis_results = options.get('analysis_results', [])
            extracted_data = options.get('extracted_data', {})

            prompt = f"""
            Synthesize all fraud detection analysis results into a comprehensive fraud assessment.
            
            Document Data:
            {json.dumps(extracted_data, indent=2, default=str)}
            
            Analysis Results:
            {json.dumps(analysis_results, indent=2, default=str)}
            
            Instructions:
            1. Review all individual fraud detection results
            2. Identify patterns and correlations between different fraud indicators
            3. Assess the overall strength and consistency of fraud evidence
            4. Calculate overall fraud confidence based on multiple indicators
            5. Determine appropriate risk level and investigation priority
            6. Provide specific recommendations for customs investigators
            
            Comprehensive Assessment Format:
            
            FRAUD DETECTION SUMMARY:
            - Overall Status: [FRAUD DETECTED / NO FRAUD DETECTED / SUSPICIOUS PATTERNS]
            - Overall Confidence: [0.0 to 1.0]
            - Risk Level: [LOW / MEDIUM / HIGH / CRITICAL]
            - Investigation Priority: [LOW / MEDIUM / HIGH / URGENT]
            
            FRAUD INDICATORS IDENTIFIED:
            [List all confirmed fraud indicators with confidence levels]
            
            EVIDENCE CORRELATION:
            [How different fraud indicators support each other]
            
            FINANCIAL IMPACT ASSESSMENT:
            - Estimated Undervaluation: $[amount]
            - Estimated Duty Evasion: $[amount]
            - Affected Trade Volume: [description]
            
            RECOMMENDED ACTIONS:
            [Specific steps for customs investigators]
            
            INVESTIGATION PRIORITIES:
            [What to focus on first]
            
            SUPPORTING EVIDENCE:
            [Key cross-document evidence compilation]
            
            Provide a thorough, actionable assessment for customs enforcement.
            """

            response = self.llm.invoke(prompt)
            return f"COMPREHENSIVE FRAUD ASSESSMENT:\n{response.content}"

        except Exception as e:
            return f"Error in fraud evidence synthesis: {str(e)}"
