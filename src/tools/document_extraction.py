"""Document extraction tool for processing raw documents into structured data."""

import json
from typing import Dict, Any, Optional, List
from langchain_openai import ChatOpenAI

from .base import BaseFraudDetectionTool
from ..models.documents import DocumentBundle, DocumentType, Document
from ..config import settings


class DocumentExtractionTool(BaseFraudDetectionTool):
    """Tool to extract structured data from raw document content."""

    _name = "extract_data_from_document"
    _description = """Extract structured data from raw document content. 
        This tool processes documents (invoices, packing lists, bills of lading, etc.) 
        and extracts key information into structured format for fraud analysis.
        Input should be document bundle data containing raw document content."""

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
        """Extract structured data from all documents in the bundle."""
        try:
            results = {}

            for document in bundle.documents:
                extracted_data = self._extract_document_data(document)
                results[document.document_type] = extracted_data

            # Format results for agent consumption
            summary = self._format_extraction_summary(results)

            return summary

        except Exception as e:
            return f"Error extracting document data: {str(e)}"

    def _extract_document_data(self, document: Document) -> Dict[str, Any]:
        """Extract structured data from a single document."""
        try:
            schema = self._get_extraction_schema(document.document_type)

            prompt = f"""
            Extract structured data from this {document.document_type} document.
            Return the data in JSON format matching this schema: {schema}
            
            Document filename: {document.filename}
            Document content:
            {document.content}
            
            Instructions:
            - Extract only the information that is clearly present in the document
            - Use null for missing or unclear information
            - Ensure all numbers are properly formatted
            - Pay special attention to quantities, weights, values, and entity information
            - For dates, use ISO format (YYYY-MM-DD)
            
            Return only valid JSON:
            """

            response = self.llm.invoke(prompt)

            # Parse the JSON response
            try:
                extracted_data = json.loads(response.content)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                content = response.content.strip()
                if content.startswith('```json'):
                    content = content[7:-3]
                elif content.startswith('```'):
                    content = content[3:-3]
                extracted_data = json.loads(content)

            return extracted_data

        except Exception as e:
            return {"error": str(e), "filename": document.filename}

    def _get_extraction_schema(self, document_type: DocumentType) -> Dict[str, Any]:
        """Get the expected schema for each document type."""
        schemas = {
            DocumentType.COMMERCIAL_INVOICE: {
                "invoice_number": "string",
                "invoice_date": "string (ISO format)",
                "supplier": {
                    "name": "string",
                    "address": "string",
                    "country": "string",
                    "tax_id": "string"
                },
                "buyer": {
                    "name": "string",
                    "address": "string",
                    "country": "string",
                    "tax_id": "string"
                },
                "items": [
                    {
                        "description": "string",
                        "quantity": "number",
                        "unit": "string",
                        "unit_price": "number",
                        "total_value": "number",
                        "weight": "number",
                        "hs_code": "string"
                    }
                ],
                "currency": "string",
                "total_value": "number",
                "payment_terms": "string",
                "incoterms": "string"
            },
            DocumentType.PACKING_LIST: {
                "packing_list_number": "string",
                "date": "string (ISO format)",
                "items": [
                    {
                        "description": "string",
                        "quantity": "number",
                        "unit": "string",
                        "weight": "number",
                        "dimensions": "string"
                    }
                ],
                "total_packages": "number",
                "total_weight": "number",
                "total_volume": "number",
                "package_details": ["string"]
            },
            DocumentType.BILL_OF_LADING: {
                "bl_number": "string",
                "date": "string (ISO format)",
                "shipper": {
                    "name": "string",
                    "address": "string",
                    "country": "string"
                },
                "consignee": {
                    "name": "string",
                    "address": "string",
                    "country": "string"
                },
                "vessel_name": "string",
                "voyage_number": "string",
                "port_of_loading": "string",
                "port_of_discharge": "string",
                "cargo_description": "string",
                "total_weight": "number",
                "number_of_packages": "number",
                "freight_terms": "string"
            },
            DocumentType.CERTIFICATE_OF_ORIGIN: {
                "certificate_number": "string",
                "issue_date": "string (ISO format)",
                "issuing_authority": "string",
                "exporter": {
                    "name": "string",
                    "address": "string",
                    "country": "string"
                },
                "consignee": {
                    "name": "string",
                    "address": "string",
                    "country": "string"
                },
                "country_of_origin": "string",
                "goods_description": "string",
                "value": "number",
                "currency": "string"
            },
            DocumentType.CUSTOMS_DECLARATION: {
                "declaration_number": "string",
                "date": "string (ISO format)",
                "declarant": {
                    "name": "string",
                    "address": "string",
                    "country": "string"
                },
                "items": [
                    {
                        "description": "string",
                        "quantity": "number",
                        "unit_price": "number",
                        "total_value": "number",
                        "hs_code": "string"
                    }
                ],
                "total_declared_value": "number",
                "currency": "string",
                "duty_calculation": {"duty_type": "amount"},
                "tariff_codes": ["string"]
            }
        }

        return schemas.get(document_type, {})

    def _format_extraction_summary(self, results: Dict[str, Any]) -> str:
        """Format extraction results for the agent."""
        summary_parts = []
        summary_parts.append("DOCUMENT EXTRACTION COMPLETED")
        summary_parts.append("=" * 40)

        for doc_type, data in results.items():
            if "error" in data:
                summary_parts.append(
                    f"\n❌ {doc_type.upper()}: Extraction failed - {data['error']}")
                continue

            summary_parts.append(
                f"\n✅ {doc_type.upper()}: Successfully extracted")

            # Add key extracted information
            if doc_type == DocumentType.COMMERCIAL_INVOICE:
                if "items" in data and data["items"]:
                    total_items = len(data["items"])
                    total_value = data.get("total_value", "Unknown")
                    currency = data.get("currency", "Unknown")
                    summary_parts.append(
                        f"   - {total_items} items, Total: {total_value} {currency}")
                    summary_parts.append(
                        f"   - Supplier: {data.get('supplier', {}).get('name', 'Unknown')}")
                    summary_parts.append(
                        f"   - Buyer: {data.get('buyer', {}).get('name', 'Unknown')}")

            elif doc_type == DocumentType.PACKING_LIST:
                if "items" in data and data["items"]:
                    total_items = len(data["items"])
                    total_weight = data.get("total_weight", "Unknown")
                    total_packages = data.get("total_packages", "Unknown")
                    summary_parts.append(
                        f"   - {total_items} items, Weight: {total_weight}kg, Packages: {total_packages}")

            elif doc_type == DocumentType.BILL_OF_LADING:
                port_loading = data.get("port_of_loading", "Unknown")
                port_discharge = data.get("port_of_discharge", "Unknown")
                total_weight = data.get("total_weight", "Unknown")
                summary_parts.append(
                    f"   - Route: {port_loading} → {port_discharge}")
                summary_parts.append(f"   - Weight: {total_weight}kg")
                summary_parts.append(
                    f"   - Shipper: {data.get('shipper', {}).get('name', 'Unknown')}")

            elif doc_type == DocumentType.CERTIFICATE_OF_ORIGIN:
                country = data.get("country_of_origin", "Unknown")
                summary_parts.append(f"   - Origin: {country}")
                summary_parts.append(
                    f"   - Authority: {data.get('issuing_authority', 'Unknown')}")

        summary_parts.append(
            "\nSTRUCTURED DATA AVAILABLE FOR CROSS-DOCUMENT ANALYSIS")

        return "\n".join(summary_parts)
