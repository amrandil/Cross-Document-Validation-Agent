"""Vision-based PDF processing utilities using LLM for comprehensive document extraction."""

import io
import base64
import asyncio
from typing import List, Optional, Dict, Any
from PIL import Image
import pdf2image
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from ..models.documents import DocumentType
from ..config import settings
from .logging_config import log_step, log_performance, log_error, log_llm, log_vision_processing, log_preprocessing_step


class VisionPDFProcessor:
    """Utility class for extracting comprehensive content from PDF files using vision-enabled LLMs."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VisionPDFProcessor, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if VisionPDFProcessor._initialized:
            return

        # Use the same model from settings as default for all tasks
        self.vision_model_name = settings.openai_model
        self.summary_model_name = settings.openai_model

        # Vision LLM for comprehensive document analysis
        self.vision_llm = ChatOpenAI(
            model=self.vision_model_name,
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=4096,  # Allow for comprehensive extraction
            api_key=settings.openai_api_key
        )

        # Summary LLM for document summarization
        self.summary_llm = ChatOpenAI(
            model=self.summary_model_name,
            temperature=0.1,  # Low temperature for consistent summaries
            api_key=settings.openai_api_key
        )

        VisionPDFProcessor._initialized = True

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of VisionPDFProcessor."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def extract_comprehensive_content_async(
        self,
        pdf_bytes: bytes,
        filename: str,
        document_type: DocumentType
    ) -> str:
        """
        Extract comprehensive content from PDF using vision-enabled LLM with streaming updates.
        """
        import time
        start_time = time.time()

        log_step("start", message="PDF vision extraction started",
                 filename=filename, doc_type=document_type, file_size=f"{len(pdf_bytes):,} bytes")

        # Stream preprocessing start
        await log_preprocessing_step("start", filename=filename,
                                     doc_type=document_type.value,
                                     file_size=f"{len(pdf_bytes):,} bytes")

        try:
            # Convert PDF to images
            log_step("preprocess", message="Converting PDF to images",
                     filename=filename)
            await log_preprocessing_step("converting_pdf", filename=filename)

            images = self._pdf_to_images(pdf_bytes)

            if not images:
                log_error("pdf_conversion_error",
                          f"No images generated for {filename}", filename=filename)
                await log_preprocessing_step("error", filename=filename,
                                             error="No images generated from PDF")
                return f"[VISION EXTRACTION FAILED - NO IMAGES GENERATED FOR {filename}]"

            log_step("preprocess", message="PDF converted to images",
                     filename=filename, pages=len(images))
            await log_preprocessing_step("pdf_converted", filename=filename, pages=len(images))

            # Process all pages with vision LLM
            all_content = []

            for page_num, image in enumerate(images, 1):
                log_step("preprocess", message=f"Processing page {page_num}/{len(images)}",
                         filename=filename, page=page_num, total_pages=len(images))

                # Stream page processing start
                await log_vision_processing(filename=filename, page=page_num,
                                            total_pages=len(images), status="started")

                page_content = await self._extract_page_content_async(
                    image,
                    page_num,
                    len(images),
                    document_type,
                    filename
                )

                if page_content:
                    all_content.append(
                        f"=== PAGE {page_num} ===\n{page_content}")
                    log_step("complete", message=f"Page {page_num} content extracted",
                             filename=filename, page=page_num, content_length=f"{len(page_content):,} chars")

                    # Stream page completion
                    await log_vision_processing(filename=filename, page=page_num,
                                                total_pages=len(images), status="completed",
                                                content_length=f"{len(page_content):,} chars")
                else:
                    log_error("page_extraction_error", f"No content extracted from page {page_num}",
                              filename=filename, page=page_num)

                    # Stream page error
                    await log_vision_processing(filename=filename, page=page_num,
                                                total_pages=len(images), status="error")

            if not all_content:
                log_error(
                    "extraction_failed", f"No content extracted from {filename}", filename=filename)
                await log_preprocessing_step("error", filename=filename,
                                             error="No content extracted from any page")
                return f"[VISION EXTRACTION FAILED - NO CONTENT EXTRACTED FROM {filename}]"

            # Combine all pages and add document summary
            log_step("preprocess", message="Combining page content",
                     filename=filename)
            await log_preprocessing_step("combining_content", filename=filename)

            combined_content = "\n\n".join(all_content)

            # Generate document summary and structure
            log_step("preprocess",
                     message="Generating document summary", filename=filename)
            await log_preprocessing_step("generating_summary", filename=filename)

            final_content = await self._generate_document_summary_async(
                combined_content,
                document_type,
                filename,
                len(images)
            )

            extraction_time = time.time() - start_time
            log_performance("pdf_vision_extraction", extraction_time,
                            filename=filename, pages=len(images))

            log_step("complete", message="PDF vision extraction completed",
                     filename=filename, final_length=f"{len(final_content):,} chars",
                     extraction_time=f"{extraction_time:.2f}s")

            # Stream completion
            await log_preprocessing_step("completed", filename=filename,
                                         final_length=f"{len(final_content):,} chars",
                                         extraction_time=f"{extraction_time:.2f}s")

            return final_content

        except Exception as e:
            extraction_time = time.time() - start_time
            log_error("vision_extraction_error", f"Vision extraction failed for {filename}",
                      filename=filename, error=str(e), extraction_time=f"{extraction_time:.2f}s")

            # Stream error
            await log_preprocessing_step("error", filename=filename,
                                         error=str(e), extraction_time=f"{extraction_time:.2f}s")

            return f"[VISION EXTRACTION ERROR FOR {filename}: {str(e)}]"

    def extract_comprehensive_content(
        self,
        pdf_bytes: bytes,
        filename: str,
        document_type: DocumentType
    ) -> str:
        """
        Synchronous wrapper for extract_comprehensive_content_async.
        """
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, run the async version
                return loop.run_until_complete(
                    self.extract_comprehensive_content_async(
                        pdf_bytes, filename, document_type)
                )
            else:
                # If no event loop is running, create a new one
                return asyncio.run(
                    self.extract_comprehensive_content_async(
                        pdf_bytes, filename, document_type)
                )
        except RuntimeError:
            # Fallback to synchronous processing if async is not available
            return self._extract_comprehensive_content_sync(pdf_bytes, filename, document_type)

    def _extract_comprehensive_content_sync(
        self,
        pdf_bytes: bytes,
        filename: str,
        document_type: DocumentType
    ) -> str:
        """
        Synchronous version of extract_comprehensive_content for fallback.
        """
        import time
        start_time = time.time()

        log_step("start", message="PDF vision extraction started",
                 filename=filename, doc_type=document_type, file_size=f"{len(pdf_bytes):,} bytes")

        try:
            # Convert PDF to images
            log_step("preprocess", message="Converting PDF to images",
                     filename=filename)
            images = self._pdf_to_images(pdf_bytes)

            if not images:
                log_error("pdf_conversion_error",
                          f"No images generated for {filename}", filename=filename)
                return f"[VISION EXTRACTION FAILED - NO IMAGES GENERATED FOR {filename}]"

            log_step("preprocess", message="PDF converted to images",
                     filename=filename, pages=len(images))

            # Process all pages with vision LLM
            all_content = []

            for page_num, image in enumerate(images, 1):
                log_step("preprocess", message=f"Processing page {page_num}/{len(images)}",
                         filename=filename, page=page_num, total_pages=len(images))

                page_content = self._extract_page_content(
                    image,
                    page_num,
                    len(images),
                    document_type,
                    filename
                )

                if page_content:
                    all_content.append(
                        f"=== PAGE {page_num} ===\n{page_content}")
                    log_step("complete", message=f"Page {page_num} content extracted",
                             filename=filename, page=page_num, content_length=f"{len(page_content):,} chars")
                else:
                    log_error("page_extraction_error", f"No content extracted from page {page_num}",
                              filename=filename, page=page_num)

            if not all_content:
                log_error(
                    "extraction_failed", f"No content extracted from {filename}", filename=filename)
                return f"[VISION EXTRACTION FAILED - NO CONTENT EXTRACTED FROM {filename}]"

            # Combine all pages and add document summary
            log_step("preprocess", message="Combining page content",
                     filename=filename)
            combined_content = "\n\n".join(all_content)

            # Generate document summary and structure
            log_step("preprocess",
                     message="Generating document summary", filename=filename)
            final_content = self._generate_document_summary(
                combined_content,
                document_type,
                filename,
                len(images)
            )

            extraction_time = time.time() - start_time
            log_performance("pdf_vision_extraction", extraction_time,
                            filename=filename, pages=len(images))

            log_step("complete", message="PDF vision extraction completed",
                     filename=filename, final_length=f"{len(final_content):,} chars",
                     extraction_time=f"{extraction_time:.2f}s")

            return final_content

        except Exception as e:
            extraction_time = time.time() - start_time
            log_error("vision_extraction_error", f"Vision extraction failed for {filename}",
                      filename=filename, error=str(e), extraction_time=f"{extraction_time:.2f}s")
            return f"[VISION EXTRACTION ERROR FOR {filename}: {str(e)}]"

    def _pdf_to_images(self, pdf_bytes: bytes) -> List[Image.Image]:
        """Convert PDF bytes to list of PIL Images."""
        try:
            # Convert PDF to images using pdf2image
            images = pdf2image.convert_from_bytes(
                pdf_bytes,
                dpi=200,  # High DPI for better text recognition
                fmt='PNG',
                thread_count=2
            )
            return images
        except Exception as e:
            return []

    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string for API."""
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str

    async def _extract_page_content_async(
        self,
        image: Image.Image,
        page_num: int,
        total_pages: int,
        document_type: DocumentType,
        filename: str
    ) -> str:
        """Extract content from a single page using vision LLM."""
        try:
            # Convert image to base64
            image_b64 = self._image_to_base64(image)

            # Get document-specific extraction prompt
            prompt = self._get_extraction_prompt(
                document_type, page_num, total_pages, filename)

            # Create message with image
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"}
                    }
                ]
            )

            # Get response from vision LLM
            response = await self.vision_llm.ainvoke([message])
            return response.content

        except Exception as e:
            return f"[PAGE {page_num} EXTRACTION FAILED: {str(e)}]"

    def _extract_page_content(
        self,
        image: Image.Image,
        page_num: int,
        total_pages: int,
        document_type: DocumentType,
        filename: str
    ) -> str:
        """Extract content from a single page using vision LLM."""
        try:
            # Convert image to base64
            image_b64 = self._image_to_base64(image)

            # Get document-specific extraction prompt
            prompt = self._get_extraction_prompt(
                document_type, page_num, total_pages, filename)

            # Create message with image
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"}
                    }
                ]
            )

            # Get response from vision LLM
            response = self.vision_llm.invoke([message])
            return response.content

        except Exception as e:
            return f"[PAGE {page_num} EXTRACTION FAILED: {str(e)}]"

    def _get_extraction_prompt(
        self,
        document_type: DocumentType,
        page_num: int,
        total_pages: int,
        filename: str
    ) -> str:
        """Generate document-specific extraction prompt for comprehensive analysis."""

        base_prompt = f"""
You are analyzing page {page_num} of {total_pages} from a {document_type.value} document ({filename}).

EXTRACT EVERYTHING visible in this image with maximum detail and accuracy. Focus on:

1. **ALL TEXT CONTENT**: Every word, number, code, reference, signature, stamp
2. **STRUCTURED DATA**: Tables, forms, lists, sections with their relationships
3. **METADATA**: Dates, document numbers, reference codes, certifications
4. **ENTITIES**: Company names, addresses, contact information, officials
5. **FINANCIAL DATA**: All amounts, currencies, calculations, totals, taxes
6. **QUANTITIES & MEASUREMENTS**: Weights, dimensions, counts, units
7. **SHIPPING/LOGISTICS**: Ports, vessels, containers, routing, tracking numbers
8. **REGULATORY INFO**: Licenses, permits, classifications, compliance codes
9. **SIGNATURES & STAMPS**: Official marks, certifications, authorizations
10. **LAYOUT CONTEXT**: How information is organized and related

"""

        # Add document-specific instructions
        specific_instructions = {
            DocumentType.COMMERCIAL_INVOICE: """
COMMERCIAL INVOICE SPECIFIC EXTRACTION:
- Invoice header: Number, date, terms, currency
- Seller/Buyer: Complete company details, addresses, tax IDs
- Line items: Product codes, descriptions, quantities, unit prices, totals
- Calculations: Subtotals, taxes, discounts, shipping, final total
- Payment terms, delivery terms, banking details
- Any certifications or regulatory information
""",

            DocumentType.BILL_OF_LADING: """
BILL OF LADING SPECIFIC EXTRACTION:
- B/L number, date, type (Master/House)
- Shipper, consignee, notify party details
- Vessel name, voyage, port of loading/discharge
- Container numbers, seal numbers, package details
- Cargo description, weight, measurement, marks
- Freight terms, delivery instructions
- Agent signatures and stamps
""",

            DocumentType.PACKING_LIST: """
PACKING LIST SPECIFIC EXTRACTION:
- Packing list number, date, reference to invoice/PO
- Detailed item breakdown: SKUs, descriptions, quantities
- Package information: boxes, cartons, pallets with contents
- Dimensions and weights (gross/net) per package
- Markings, labels, handling instructions
- Total quantities and package counts
""",

            DocumentType.CERTIFICATE_OF_ORIGIN: """
CERTIFICATE OF ORIGIN SPECIFIC EXTRACTION:
- Certificate number, issuing authority, date
- Exporter/producer information and addresses
- Consignee details and destination country
- Detailed goods description and origin criteria
- HS codes, quantities, values
- Declaration statements and legal text
- Official signatures, stamps, seals
""",

            DocumentType.CUSTOMS_DECLARATION: """
CUSTOMS DECLARATION SPECIFIC EXTRACTION:
- Declaration number, date, customs office
- Importer/exporter details and codes
- Detailed goods classification and values
- Duty calculations and payment information
- Supporting document references
- Official processing stamps and signatures
"""
        }

        document_specific = specific_instructions.get(
            document_type,
            "GENERAL DOCUMENT: Extract all visible information systematically."
        )

        return base_prompt + document_specific + """

IMPORTANT INSTRUCTIONS:
- Preserve exact numbers, dates, and codes - accuracy is critical for fraud detection
- Maintain table structure and relationships between data points
- Note any inconsistencies, corrections, or unusual markings
- If text is unclear, indicate [UNCLEAR] but attempt best interpretation
- Organize output in clear sections with headers
- Include page layout context (where information appears)

Provide comprehensive, structured extraction suitable for fraud detection analysis.
"""

    async def _generate_document_summary_async(
        self,
        combined_content: str,
        document_type: DocumentType,
        filename: str,
        page_count: int
    ) -> str:
        """Generate a comprehensive document summary with key data points."""

        summary_prompt = f"""
Based on the comprehensive page-by-page extraction below, create a MASTER DOCUMENT SUMMARY for this {document_type.value} ({filename}, {page_count} pages).

PROVIDE:
1. **DOCUMENT OVERVIEW**: Type, number, date, parties involved
2. **KEY DATA EXTRACTION**: All critical numbers, amounts, quantities, dates
3. **ENTITY INFORMATION**: All companies, addresses, contacts, officials
4. **TRANSACTION DETAILS**: Products, services, financial terms, logistics
5. **REGULATORY DATA**: Certifications, codes, compliance information
6. **CROSS-REFERENCES**: Links between different data points
7. **FRAUD DETECTION FOCUS**: Highlight data points critical for fraud analysis

STRUCTURE THE SUMMARY FOR MAXIMUM UTILITY IN FRAUD DETECTION ANALYSIS.

Original extracted content:
{combined_content}
"""

        try:
            # Use the instance summary LLM
            response = await self.summary_llm.ainvoke(summary_prompt)

            # Combine summary with original content
            final_content = f"""
=== COMPREHENSIVE DOCUMENT ANALYSIS ===
Document: {filename}
Type: {document_type.value}
Pages: {page_count}
Extraction Method: Vision LLM Analysis

{response.content}

=== DETAILED PAGE-BY-PAGE EXTRACTION ===
{combined_content}
"""
            return final_content

        except Exception as e:
            # Return original content if summary fails
            return f"""
=== DOCUMENT EXTRACTION ===
Document: {filename}
Type: {document_type.value}
Pages: {page_count}
Note: Summary generation failed, showing detailed extraction only

{combined_content}
"""

    def _generate_document_summary(
        self,
        combined_content: str,
        document_type: DocumentType,
        filename: str,
        page_count: int
    ) -> str:
        """Generate a comprehensive document summary with key data points."""

        summary_prompt = f"""
Based on the comprehensive page-by-page extraction below, create a MASTER DOCUMENT SUMMARY for this {document_type.value} ({filename}, {page_count} pages).

PROVIDE:
1. **DOCUMENT OVERVIEW**: Type, number, date, parties involved
2. **KEY DATA EXTRACTION**: All critical numbers, amounts, quantities, dates
3. **ENTITY INFORMATION**: All companies, addresses, contacts, officials
4. **TRANSACTION DETAILS**: Products, services, financial terms, logistics
5. **REGULATORY DATA**: Certifications, codes, compliance information
6. **CROSS-REFERENCES**: Links between different data points
7. **FRAUD DETECTION FOCUS**: Highlight data points critical for fraud analysis

STRUCTURE THE SUMMARY FOR MAXIMUM UTILITY IN FRAUD DETECTION ANALYSIS.

Original extracted content:
{combined_content}
"""

        try:
            # Use the instance summary LLM
            response = self.summary_llm.invoke(summary_prompt)

            # Combine summary with original content
            final_content = f"""
=== COMPREHENSIVE DOCUMENT ANALYSIS ===
Document: {filename}
Type: {document_type.value}
Pages: {page_count}
Extraction Method: Vision LLM Analysis

{response.content}

=== DETAILED PAGE-BY-PAGE EXTRACTION ===
{combined_content}
"""
            return final_content

        except Exception as e:
            # Return original content if summary fails
            return f"""
=== DOCUMENT EXTRACTION ===
Document: {filename}
Type: {document_type.value}
Pages: {page_count}
Note: Summary generation failed, showing detailed extraction only

{combined_content}
"""

    @staticmethod
    def is_pdf(file_bytes: bytes) -> bool:
        """Check if the file bytes represent a PDF file."""
        return file_bytes.startswith(b'%PDF')

    def get_processor_info(self) -> Dict[str, Any]:
        """Get information about the vision processor."""
        return {
            "processor_type": "Vision LLM PDF Processor",
            "vision_model": self.vision_model_name,
            "summary_model": self.summary_model_name,
            "capabilities": [
                "PDF to image conversion",
                "Vision-based text extraction",
                "Structured data recognition",
                "Document-specific analysis",
                "Comprehensive content extraction",
                "Fraud detection optimization"
            ]
        }

    def update_vision_model(self, new_model: str) -> None:
        """Update the vision model used for document extraction."""
        try:
            # Test the new model
            test_llm = ChatOpenAI(
                model=new_model,
                temperature=0.1,
                max_tokens=4096,
                api_key=settings.openai_api_key
            )

            # Test with a simple text message to validate the model
            test_message = HumanMessage(content="Test message")
            test_llm.invoke([test_message])

            # Update if successful
            self.vision_model_name = new_model
            self.vision_llm = test_llm

        except Exception as e:
            raise ValueError(f"Invalid vision model '{new_model}': {str(e)}")

    def update_summary_model(self, new_model: str) -> None:
        """Update the summary model used for document summarization."""
        try:
            # Test the new model
            test_llm = ChatOpenAI(
                model=new_model,
                temperature=0.1,
                api_key=settings.openai_api_key
            )

            # Test with a simple message to validate the model
            test_message = "Test message"
            test_llm.invoke(test_message)

            # Update if successful
            self.summary_model_name = new_model
            self.summary_llm = test_llm

        except Exception as e:
            raise ValueError(f"Invalid summary model '{new_model}': {str(e)}")
