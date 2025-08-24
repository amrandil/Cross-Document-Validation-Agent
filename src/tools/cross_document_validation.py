"""Cross-document validation tools for fraud detection."""

import json
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI

from .base import BaseFraudDetectionTool
from ..models.documents import DocumentBundle, DocumentType
from ..config import settings
from ..utils.logging_config import workflow_logger


class QuantityConsistencyTool(BaseFraudDetectionTool):
    """Tool to validate quantity consistency across documents."""

    _name = "validate_quantity_consistency"
    _description = """Validate that quantities are consistent across all documents (invoice, packing list, bill of lading).
        This tool identifies quantity discrepancies that may indicate fraudulent manipulation."""

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
        """Check quantity consistency across documents."""
        try:
            # Get extracted data from all documents
            extracted_data = options.get('extracted_data', {})

            prompt = f"""
            Analyze the quantity information across these customs documents to identify any inconsistencies that could indicate fraud.
            
            Document Data:
            {json.dumps(extracted_data, indent=2, default=str)}
            
            Instructions:
            1. Compare quantities for the same products across all documents
            2. Look for discrepancies between invoice quantities, packing list quantities, and bill of lading quantities
            3. Identify products that appear in some documents but not others
            4. Calculate total quantities and identify any mismatches
            5. Assess the severity of any inconsistencies found
            
            Provide a detailed analysis including:
            - PASS/FAIL status for quantity consistency
            - Specific discrepancies found (if any)
            - Fraud risk assessment
            - Confidence level (0.0 to 1.0)
            
            Format the response clearly for customs investigators.
            """

            response = self.llm.invoke(prompt)
            return f"QUANTITY CONSISTENCY ANALYSIS:\n{response.content}"

        except Exception as e:
            # Log detailed error information
            workflow_logger.log_error(
                error_type="validation_error",
                error_message=f"Quantity consistency validation failed: {str(e)}",
                tool="validate_quantity_consistency",
                bundle_id=getattr(bundle, 'id', 'unknown'),
                exception_type=type(e).__name__,
                extracted_data_keys=list(
                    extracted_data.keys()) if extracted_data else []
            )

            return f"Error in quantity consistency validation: {str(e)}"


class WeightConsistencyTool(BaseFraudDetectionTool):
    """Tool to validate weight consistency across documents."""

    _name = "validate_weight_consistency"
    _description = """Validate that weights are consistent across all documents.
        This tool identifies weight discrepancies that may indicate product substitution or quantity manipulation."""

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
        """Check weight consistency across documents."""
        try:
            extracted_data = options.get('extracted_data', {})

            prompt = f"""
            Analyze the weight information across these customs documents for inconsistencies.
            
            Document Data:
            {json.dumps(extracted_data, indent=2, default=str)}
            
            Instructions:
            1. Compare total weights across packing list and bill of lading
            2. Calculate weight per unit for products and identify anomalies
            3. Check if individual item weights sum to total weights
            4. Identify any significant weight discrepancies
            5. Assess if weights are reasonable for the declared products
            
            Analysis should include:
            - Weight consistency status (PASS/FAIL)
            - Total weight comparisons
            - Per-unit weight analysis
            - Identification of suspicious weight patterns
            - Fraud confidence assessment
            
            Provide clear findings for customs investigators.
            """

            response = self.llm.invoke(prompt)
            return f"WEIGHT CONSISTENCY ANALYSIS:\n{response.content}"

        except Exception as e:
            # Log detailed error information
            workflow_logger.log_error(
                error_type="validation_error",
                error_message=f"Weight consistency validation failed: {str(e)}",
                tool="validate_weight_consistency",
                bundle_id=getattr(bundle, 'id', 'unknown'),
                exception_type=type(e).__name__,
                extracted_data_keys=list(
                    extracted_data.keys()) if extracted_data else []
            )

            return f"Error in weight consistency validation: {str(e)}"


class EntityConsistencyTool(BaseFraudDetectionTool):
    """Tool to validate entity consistency across documents."""

    _name = "validate_entity_consistency"
    _description = """Validate that entity information (suppliers, buyers, shippers) is consistent across documents.
        This tool identifies entity mismatches that may indicate fraudulent misrepresentation."""

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
        """Check entity consistency across documents."""
        try:
            extracted_data = options.get('extracted_data', {})

            prompt = f"""
            Analyze entity information (companies, suppliers, buyers, shippers) across these documents for inconsistencies.
            
            Document Data:
            {json.dumps(extracted_data, indent=2, default=str)}
            
            Instructions:
            1. Compare supplier/shipper information across all documents
            2. Verify buyer/consignee consistency
            3. Check for address and country mismatches
            4. Identify any suspicious entity variations
            5. Look for signs of entity misrepresentation
            
            Analysis should cover:
            - Entity consistency status (PASS/FAIL)  
            - Name variations or mismatches
            - Address and country discrepancies
            - Potential entity misrepresentation indicators
            - Geographic fraud risk assessment
            
            Provide detailed findings for investigation.
            """

            response = self.llm.invoke(prompt)
            return f"ENTITY CONSISTENCY ANALYSIS:\n{response.content}"

        except Exception as e:
            # Log detailed error information
            workflow_logger.log_error(
                error_type="validation_error",
                error_message=f"Entity consistency validation failed: {str(e)}",
                tool="validate_entity_consistency",
                bundle_id=getattr(bundle, 'id', 'unknown'),
                exception_type=type(e).__name__,
                extracted_data_keys=list(
                    extracted_data.keys()) if extracted_data else []
            )

            return f"Error in entity consistency validation: {str(e)}"


class ProductDescriptionTool(BaseFraudDetectionTool):
    """Tool to validate product description consistency."""

    _name = "validate_product_descriptions"
    _description = """Validate that product descriptions are consistent across documents.
        This tool identifies product description variations that may indicate product substitution fraud."""

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
        """Check product description consistency."""
        try:
            extracted_data = options.get('extracted_data', {})

            # Log validation start
            workflow_logger.log_workflow_step(
                "validation_start",
                tool="validate_product_descriptions",
                documents_count=len(extracted_data),
                bundle_id=getattr(bundle, 'id', 'unknown')
            )

            prompt = f"""
            Analyze product descriptions across these documents for inconsistencies that might indicate product substitution fraud.

            Document Data:
            {json.dumps(extracted_data, indent=2, default=str)}

            Instructions:
            1. Compare product descriptions across invoice, packing list, and other documents
            2. Identify subtle variations that might indicate product substitution
            3. Look for quality descriptors that don't match (basic vs premium, standard vs deluxe)
            4. Check if additional components/accessories are mentioned in some documents but not others
            5. Assess if descriptions match the declared values and weights

            Analysis should include:
            - Product description consistency (PASS/FAIL)
            - Specific description variations found
            - Signs of product substitution
            - Value-to-description alignment assessment
            - Product substitution fraud confidence

            Focus on detecting sophisticated product substitution schemes.
            """

            response = self.llm.invoke(prompt)

            # Log successful completion
            workflow_logger.log_workflow_step(
                "validation_complete",
                tool="validate_product_descriptions",
                response_length=len(response.content),
                success=True
            )

            return f"PRODUCT DESCRIPTION ANALYSIS:\n{response.content}"

        except Exception as e:
            # Log detailed error information
            workflow_logger.log_error(
                error_type="validation_error",
                error_message=f"Product description validation failed: {str(e)}",
                tool="validate_product_descriptions",
                bundle_id=getattr(bundle, 'id', 'unknown'),
                exception_type=type(e).__name__,
                extracted_data_keys=list(
                    extracted_data.keys()) if extracted_data else []
            )

            return f"Error in product description validation: {str(e)}"


class ValueConsistencyTool(BaseFraudDetectionTool):
    """Tool to validate value consistency across documents."""

    _name = "validate_value_consistency"
    _description = """Validate that declared values are consistent across documents.
        This tool identifies value discrepancies that may indicate undervaluation fraud."""

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
        """Check value consistency across documents."""
        try:
            extracted_data = options.get('extracted_data', {})

            # Log validation start
            workflow_logger.log_workflow_step(
                "validation_start",
                tool="validate_value_consistency",
                documents_count=len(extracted_data),
                bundle_id=getattr(bundle, 'id', 'unknown')
            )

            prompt = f"""
            Analyze declared values across these documents for inconsistencies indicating potential undervaluation fraud.

            Document Data:
            {json.dumps(extracted_data, indent=2, default=str)}

            Instructions:
            1. Compare total values between invoice and certificate of origin (if present)
            2. Verify that individual item values sum to total values
            3. Check for unreasonably low unit prices
            4. Identify any value discrepancies across documents
            5. Look for signs of systematic undervaluation

            Analysis should cover:
            - Value consistency status (PASS/FAIL)
            - Mathematical accuracy of calculations
            - Unit price reasonableness assessment
            - Cross-document value comparison
            - Undervaluation fraud indicators
            - Confidence assessment

            Provide clear findings for customs valuation review.
            """

            response = self.llm.invoke(prompt)

            # Log successful completion
            workflow_logger.log_workflow_step(
                "validation_complete",
                tool="validate_value_consistency",
                response_length=len(response.content),
                success=True
            )

            return f"VALUE CONSISTENCY ANALYSIS:\n{response.content}"

        except Exception as e:
            # Log detailed error information
            workflow_logger.log_error(
                error_type="validation_error",
                error_message=f"Value consistency validation failed: {str(e)}",
                tool="validate_value_consistency",
                bundle_id=getattr(bundle, 'id', 'unknown'),
                exception_type=type(e).__name__,
                extracted_data_keys=list(
                    extracted_data.keys()) if extracted_data else []
            )

            return f"Error in value consistency validation: {str(e)}"


class GeographicConsistencyTool(BaseFraudDetectionTool):
    """Tool to validate geographic consistency for origin fraud detection."""

    _name = "validate_geographic_consistency"
    _description = """Validate geographic consistency to detect origin manipulation and transshipment fraud.
        This tool identifies geographic inconsistencies that may indicate false origin certificates."""

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
        """Check geographic consistency across documents."""
        try:
            extracted_data = options.get('extracted_data', {})

            # Log validation start
            workflow_logger.log_workflow_step(
                "validation_start",
                tool="validate_geographic_consistency",
                documents_count=len(extracted_data),
                bundle_id=getattr(bundle, 'id', 'unknown')
            )

            prompt = f"""
            Analyze geographic information across these documents to detect origin manipulation or transshipment fraud.

            Document Data:
            {json.dumps(extracted_data, indent=2, default=str)}

            Instructions:
            1. Compare country of origin across certificate of origin and other documents
            2. Verify that shipping routes align with declared origin
            3. Check if supplier/exporter locations match country of origin
            4. Identify any geographic inconsistencies in the shipping chain
            5. Look for signs of transshipment to obscure true origin

            Analysis should include:
            - Geographic consistency status (PASS/FAIL)
            - Origin country verification
            - Shipping route analysis
            - Supplier location alignment
            - Transshipment fraud indicators
            - Geographic fraud confidence assessment

            Focus on detecting sophisticated origin manipulation schemes.
            """

            response = self.llm.invoke(prompt)

            # Log successful completion
            workflow_logger.log_workflow_step(
                "validation_complete",
                tool="validate_geographic_consistency",
                response_length=len(response.content),
                success=True
            )

            return f"GEOGRAPHIC CONSISTENCY ANALYSIS:\n{response.content}"

        except Exception as e:
            # Log detailed error information
            workflow_logger.log_error(
                error_type="validation_error",
                error_message=f"Geographic consistency validation failed: {str(e)}",
                tool="validate_geographic_consistency",
                bundle_id=getattr(bundle, 'id', 'unknown'),
                exception_type=type(e).__name__,
                extracted_data_keys=list(
                    extracted_data.keys()) if extracted_data else []
            )

            return f"Error in geographic consistency validation: {str(e)}"


class TimingAnomalyTool(BaseFraudDetectionTool):
    """Tool to detect timing anomalies across documents."""

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )

    @property
    def name(self) -> str:
        return "detect_timing_anomalies"

    @property
    def description(self) -> str:
        return """Detect timing anomalies across documents that may indicate backdating or document manipulation.
        This tool identifies suspicious date patterns in document sequences."""

    def _execute(self, bundle: DocumentBundle, options: Dict[str, Any]) -> str:
        """Check for timing anomalies across documents."""
        try:
            extracted_data = options.get('extracted_data', {})

            prompt = f"""
            Analyze dates across these documents to identify timing anomalies that might indicate document manipulation.
            
            Document Data:
            {json.dumps(extracted_data, indent=2, default=str)}
            
            Instructions:
            1. Check logical sequence of document dates (invoice → packing → shipping → certificate)
            2. Identify any backdated documents
            3. Look for unreasonably tight or loose timing between documents
            4. Verify that shipping dates align with document issuance
            5. Detect any suspicious date patterns
            
            Analysis should cover:
            - Document timing consistency (PASS/FAIL)
            - Logical sequence verification  
            - Identification of backdated documents
            - Suspicious timing patterns
            - Document manipulation indicators
            - Timing fraud confidence assessment
            
            Provide findings for document authenticity review.
            """

            response = self.llm.invoke(prompt)
            return f"TIMING ANOMALY ANALYSIS:\n{response.content}"

        except Exception as e:
            # Log detailed error information
            workflow_logger.log_error(
                error_type="validation_error",
                error_message=f"Timing anomaly detection failed: {str(e)}",
                tool="detect_timing_anomalies",
                bundle_id=getattr(bundle, 'id', 'unknown'),
                exception_type=type(e).__name__,
                extracted_data_keys=list(
                    extracted_data.keys()) if extracted_data else []
            )

            return f"Error in timing anomaly detection: {str(e)}"
