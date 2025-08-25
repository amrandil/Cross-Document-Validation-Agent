"""Direct PDF processing utilities using OpenAI's vision models for comprehensive document extraction."""

import io
import base64
import asyncio
from typing import List, Optional, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

from ..models.documents import DocumentType
from ..config import settings
from .logging_config import log_step, log_performance, log_error, log_llm, log_vision_processing, log_preprocessing_step


class VisionPDFProcessor:
    """Utility class for extracting comprehensive content from PDF files using OpenAI's direct PDF processing."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VisionPDFProcessor, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if VisionPDFProcessor._initialized:
            return

        # Load environment variables
        load_dotenv()

        # Use GPT-4o as default model for all tasks
        self.vision_model_name = "gpt-4o"
        self.summary_model_name = "gpt-4o"

        # Initialize OpenAI client
        self.client = OpenAI()

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
        Extract comprehensive content from PDF using OpenAI's direct PDF processing with streaming updates.
        """
        import time
        start_time = time.time()

        log_step("start", message="PDF direct extraction started",
                 filename=filename, doc_type=document_type, file_size=f"{len(pdf_bytes):,} bytes")

        # Stream preprocessing start
        await log_preprocessing_step("start", filename=filename,
                                     doc_type=document_type.value,
                                     file_size=f"{len(pdf_bytes):,} bytes",
                                     message="Starting direct PDF processing with OpenAI")

        # Small delay to ensure the update is sent
        await asyncio.sleep(0.1)

        try:
            # Process PDF directly using file upload method
            log_step("preprocess", message="Processing PDF directly with OpenAI",
                     filename=filename)
            await log_preprocessing_step("uploading_pdf", filename=filename,
                                         message="Uploading PDF file to OpenAI servers")

            # Small delay to ensure the update is sent
            await asyncio.sleep(0.1)

            # Upload PDF file
            file = self.client.files.create(
                file=(filename, io.BytesIO(pdf_bytes).read(), "application/pdf"),
                purpose="assistants"
            )

            log_step("preprocess", message="PDF file uploaded successfully",
                     filename=filename, file_id=file.id)
            await log_preprocessing_step("pdf_uploaded", filename=filename,
                                         file_id=file.id,
                                         message="PDF file uploaded successfully")

            # Small delay to ensure the update is sent
            await asyncio.sleep(0.1)

            # Get document-specific extraction prompt
            prompt = self._get_extraction_prompt(document_type, filename)

            await log_preprocessing_step("extracting_content", filename=filename,
                                         message=f"Extracting content using {self.vision_model_name}")

            # Small delay to ensure the update is sent
            await asyncio.sleep(0.1)

            # Create chat completion with uploaded file
            response = self.client.chat.completions.create(
                model=self.vision_model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "file",
                                "file": {
                                    "file_id": file.id,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt,
                            },
                        ]
                    }
                ],
                max_tokens=4096,
                temperature=0.1
            )

            extracted_content = response.choices[0].message.content

            if not extracted_content:
                log_error("extraction_failed",
                          f"No content extracted from {filename}", filename=filename)
                await log_preprocessing_step("error", filename=filename,
                                             error="No content extracted from PDF",
                                             message="PDF extraction failed - no content found")
                return f"[PDF EXTRACTION FAILED - NO CONTENT EXTRACTED FROM {filename}]"

            log_step("preprocess", message="PDF content extracted successfully",
                     filename=filename, content_length=f"{len(extracted_content):,} chars")
            await log_preprocessing_step("content_extracted", filename=filename,
                                         content_length=f"{len(extracted_content):,} chars",
                                         message="PDF content extracted successfully")

            # Small delay to ensure the update is sent
            await asyncio.sleep(0.1)

            # Generate document summary and structure
            # log_step("preprocess",
            #         message="Generating document summary", filename=filename)
            # await log_preprocessing_step("generating_summary", filename=filename,
            #                             message="Generating comprehensive document summary")

            # Small delay to ensure the update is sent
            # await asyncio.sleep(0.1)

            # final_content = await self._generate_document_summary_async(
            #    extracted_content,
            #    document_type,
            #    filename
            # )

            extraction_time = time.time() - start_time
            log_performance("pdf_direct_extraction", extraction_time,
                            filename=filename)

            log_step("complete", message="PDF direct extraction completed",
                     filename=filename, final_length=f"{len(extracted_content):,} chars",
                     extraction_time=f"{extraction_time:.2f}s")

            # Stream completion
            await log_preprocessing_step("completed", filename=filename,
                                         final_length=f"{len(extracted_content):,} chars",
                                         extraction_time=f"{extraction_time:.2f}s",
                                         message="PDF processing completed successfully")

            # Clean up uploaded file
            try:
                self.client.files.delete(file.id)
                log_step("cleanup", message="Uploaded file deleted",
                         filename=filename, file_id=file.id)
            except Exception as e:
                log_error("file_cleanup_error", f"Failed to delete uploaded file {file.id}",
                          filename=filename, error=str(e))

            # return final_content
            return extracted_content

        except Exception as e:
            extraction_time = time.time() - start_time
            log_error("direct_extraction_error", f"Direct PDF extraction failed for {filename}",
                      filename=filename, error=str(e), extraction_time=f"{extraction_time:.2f}s")

            # Stream error
            await log_preprocessing_step("error", filename=filename,
                                         error=str(e), extraction_time=f"{extraction_time:.2f}s",
                                         message=f"PDF processing failed: {str(e)}")

            return f"[PDF DIRECT EXTRACTION ERROR FOR {filename}: {str(e)}]"

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

        log_step("start", message="PDF direct extraction started (sync)",
                 filename=filename, doc_type=document_type, file_size=f"{len(pdf_bytes):,} bytes")

        try:
            # Process PDF directly using file upload method
            log_step("preprocess", message="Processing PDF directly with OpenAI (sync)",
                     filename=filename)

            # Upload PDF file
            file = self.client.files.create(
                file=(filename, io.BytesIO(pdf_bytes).read(), "application/pdf"),
                purpose="assistants"
            )

            log_step("preprocess", message="PDF file uploaded successfully (sync)",
                     filename=filename, file_id=file.id)

            # Get document-specific extraction prompt
            prompt = self._get_extraction_prompt(document_type, filename)

            # Create chat completion with uploaded file
            response = self.client.chat.completions.create(
                model=self.vision_model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "file",
                                "file": {
                                    "file_id": file.id,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt,
                            },
                        ]
                    }
                ],
                max_tokens=4096,
                temperature=0.1
            )

            extracted_content = response.choices[0].message.content

            if not extracted_content:
                log_error("extraction_failed",
                          f"No content extracted from {filename}", filename=filename)
                return f"[PDF EXTRACTION FAILED - NO CONTENT EXTRACTED FROM {filename}]"

            log_step("preprocess", message="PDF content extracted successfully (sync)",
                     filename=filename, content_length=f"{len(extracted_content):,} chars")

            # Generate document summary and structure
            log_step("preprocess",
                     message="Generating document summary (sync)", filename=filename)
            final_content = self._generate_document_summary(
                extracted_content,
                document_type,
                filename
            )

            extraction_time = time.time() - start_time
            log_performance("pdf_direct_extraction_sync", extraction_time,
                            filename=filename)

            log_step("complete", message="PDF direct extraction completed (sync)",
                     filename=filename, final_length=f"{len(final_content):,} chars",
                     extraction_time=f"{extraction_time:.2f}s")

            # Clean up uploaded file
            try:
                self.client.files.delete(file.id)
                log_step("cleanup", message="Uploaded file deleted (sync)",
                         filename=filename, file_id=file.id)
            except Exception as e:
                log_error("file_cleanup_error", f"Failed to delete uploaded file {file.id}",
                          filename=filename, error=str(e))

            return final_content

        except Exception as e:
            extraction_time = time.time() - start_time
            log_error("direct_extraction_error", f"Direct PDF extraction failed for {filename} (sync)",
                      filename=filename, error=str(e), extraction_time=f"{extraction_time:.2f}s")
            return f"[PDF DIRECT EXTRACTION ERROR FOR {filename}: {str(e)}]"

    def _get_extraction_prompt(
        self,
        document_type: DocumentType,
        filename: str
    ) -> str:
        """Generate document-specific extraction prompt for comprehensive analysis."""

        base_prompt = """
            # System Prompt: Complete Document Data Extraction

            ## Primary Objective
            Your task is to perform **COMPLETE AND EXHAUSTIVE** extraction of ALL textual content from any document provided. You must capture every single piece of visible text, number, code, symbol, and data element without exception.

            ## Core Principle: CAPTURE EVERYTHING
            **DO NOT SELECTIVELY EXTRACT** - Read and transcribe the entire document from top to bottom, left to right. Treat every character, word, number, and symbol as potentially important.

            ## Fundamental Rules

            ### 1. Total Coverage Requirement
            - Extract **100% of all visible text** in the document
            - Include headers, footers, watermarks, and marginal text
            - Capture form field labels AND their values
            - Include all numbers, codes, references, and identifiers
            - Transcribe all company names, addresses, and contact information
            - Record all dates, times, and temporal references
            - Include all monetary amounts and calculations
            - Capture all product descriptions and specifications
            - Include all terms, conditions, and legal text
            - Record all signatures, stamps, and authorization elements

            ### 2. Structural Preservation
            - Maintain the **exact visual organization** of the document
            - Preserve table structures with proper row/column alignment
            - Maintain list hierarchies and numbering systems
            - Keep form layouts and field relationships intact
            - Preserve spatial relationships between elements
            - Maintain the logical flow from top to bottom, left to right

            ### 3. Page-by-Page Processing
            For multi-page documents:
            - Process each page completely before moving to the next
            - Clearly mark page boundaries
            - Maintain document continuity and context
            - Note any page headers/footers that repeat
            - Preserve cross-page references and relationships

            ## Output Format Requirements

            Structure your output as follows:

            ```markdown
            # Complete Document Extraction

            ## Document Summary
            - **Total Pages**: [number]
            - **Document Characteristics**: [brief description of document type/layout]
            - **Extraction Date**: [current date]

            ---

            ## PAGE 1

            [Transcribe EVERY element on page 1 in reading order - top to bottom, left to right]

            ### [Section Name if identifiable]
            [All content in this section]

            ### [Next Section Name]
            [All content in this section]

            [Continue until page 1 is completely captured]

            ---

            ## PAGE 2

            [Transcribe EVERY element on page 2 in the same manner]

            [Continue for all pages...]

            ---


            ```

            ## Specific Processing Instructions

            ### Text Processing
            - **Read systematically**: Start from the top-left, move right, then down
            - **Miss nothing**: Include seemingly insignificant text like form numbers, revision dates, small print
            - **Maintain context**: Keep related information together when possible
            - **Preserve formatting**: Use appropriate markdown to maintain visual structure

            ### Table Handling
            When encountering tables:
            1. **Identify the complete table structure** including all headers and subheaders
            2. **Capture every cell** - including empty cells (mark as [EMPTY])
            3. **Preserve merged cells** and spanning elements
            4. **Include all totals, subtotals, and calculations**
            5. **Use proper markdown table format** to maintain readability

            ### Forms and Fields
            For forms and structured layouts:
            - **Extract both labels and values**: "Field Name: Value" or "Field Name: [BLANK]"
            - **Include checkbox states**: [✓] for checked, [ ] for unchecked
            - **Capture dropdown selections** and available options when visible
            - **Note any handwritten entries** or annotations

            ### Handling Unclear Content
            - **Unclear text**: `[UNCLEAR: best_guess]`
            - **Completely illegible**: `[ILLEGIBLE]`
            - **Partially visible**: `[PARTIAL: visible_portion...]`
            - **Empty fields**: `[BLANK]` or `[EMPTY]`
            - **Damaged areas**: `[DAMAGED]`

            ## Quality Assurance Protocol

            ### Before Submitting Your Extraction:

            1. **Completeness Check**:
            - Scan through the original document page by page
            - Verify that every visible text element has been captured
            - Ensure no sections have been skipped or summarized

            2. **Accuracy Verification**:
            - Double-check all numbers and codes for exact transcription
            - Verify proper names and addresses are correctly spelled
            - Confirm all currency amounts and calculations

            3. **Structure Validation**:
            - Ensure tables are properly formatted and complete
            - Verify that page breaks are clearly marked
            - Confirm that the reading flow is logical and complete

            ## Critical Success Factors

            ### What Makes a Perfect Extraction:
            - **Exhaustiveness**: Nothing visible in the document is missing from your extraction
            - **Accuracy**: Every character, number, and symbol is correctly transcribed
            - **Organization**: Information is presented in a logical, readable structure
            - **Completeness**: All pages are fully processed without gaps or omissions

            ### Common Mistakes to Avoid:
            - Summarizing instead of transcribing
            - Skipping "unimportant" text or fine print
            - Focusing only on main content while missing headers/footers
            - Incomplete table extraction
            - Missing form field labels or values
            - Omitting reference numbers, codes, or identifiers
            - Failing to capture all contact information and addresses

            ## Final Instruction

            - Your goal is to create an extraction so complete and accurate that someone could reconstruct the essential content and structure of the original document using only your text output. **Leave nothing behind.**
            - Don't add concluding messages/questions to the user.

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
        # return base_prompt + document_specific + """
        return base_prompt + """
            IMPORTANT INSTRUCTIONS:
            - Preserve exact numbers, dates, and codes - accuracy is critical for fraud detection
            - Maintain table structure and relationships between data points
            - Note any inconsistencies, corrections, or unusual markings
            - If text is unclear, indicate [UNCLEAR] but attempt best interpretation
            - Organize output in clear sections with headers
            - Include document layout context (where information appears)
            - Extract content from ALL pages of the PDF

            Provide comprehensive, structured extraction suitable for fraud detection analysis.
        """

    async def _generate_document_summary_async(
        self,
        extracted_content: str,
        document_type: DocumentType,
        filename: str
    ) -> str:
        """Generate a comprehensive document summary with key data points."""

        summary_prompt = f"""
Based on the comprehensive PDF extraction below, create a MASTER DOCUMENT SUMMARY for this {document_type.value} ({filename}).

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
{extracted_content}
"""

        try:
            # Use OpenAI client for summary generation
            response = self.client.chat.completions.create(
                model=self.summary_model_name,
                messages=[
                    {
                        "role": "user",
                        "content": summary_prompt
                    }
                ],
                max_tokens=2048,
                temperature=0.1
            )

            summary_content = response.choices[0].message.content

            # Combine summary with original content
            final_content = f"""
=== COMPREHENSIVE DOCUMENT ANALYSIS ===
Document: {filename}
Type: {document_type.value}
Extraction Method: OpenAI Direct PDF Processing
Model: {self.vision_model_name}

{summary_content}

=== DETAILED PDF EXTRACTION ===
{extracted_content}
"""
            return final_content

        except Exception as e:
            # Return original content if summary fails
            return f"""
=== DOCUMENT EXTRACTION ===
Document: {filename}
Type: {document_type.value}
Note: Summary generation failed, showing detailed extraction only

{extracted_content}
"""

    def _generate_document_summary(
        self,
        extracted_content: str,
        document_type: DocumentType,
        filename: str
    ) -> str:
        """Generate a comprehensive document summary with key data points."""

        summary_prompt = f"""
Based on the comprehensive PDF extraction below, create a MASTER DOCUMENT SUMMARY for this {document_type.value} ({filename}).

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
{extracted_content}
"""

        try:
            # Use OpenAI client for summary generation
            response = self.client.chat.completions.create(
                model=self.summary_model_name,
                messages=[
                    {
                        "role": "user",
                        "content": summary_prompt
                    }
                ],
                max_tokens=2048,
                temperature=0.1
            )

            summary_content = response.choices[0].message.content

            # Combine summary with original content
            final_content = f"""
=== COMPREHENSIVE DOCUMENT ANALYSIS ===
Document: {filename}
Type: {document_type.value}
Extraction Method: OpenAI Direct PDF Processing
Model: {self.vision_model_name}

{summary_content}

=== DETAILED PDF EXTRACTION ===
{extracted_content}
"""
            return final_content

        except Exception as e:
            # Return original content if summary fails
            return f"""
=== DOCUMENT EXTRACTION ===
Document: {filename}
Type: {document_type.value}
Note: Summary generation failed, showing detailed extraction only

{extracted_content}
"""

    @staticmethod
    def is_pdf(file_bytes: bytes) -> bool:
        """Check if the file bytes represent a PDF file."""
        return file_bytes.startswith(b'%PDF')

    def get_processor_info(self) -> Dict[str, Any]:
        """Get information about the vision processor."""
        return {
            "processor_type": "OpenAI Direct PDF Processor",
            "vision_model": self.vision_model_name,
            "summary_model": self.summary_model_name,
            "capabilities": [
                "Direct PDF processing (no image conversion)",
                "Vision-based text extraction",
                "Structured data recognition",
                "Document-specific analysis",
                "Comprehensive content extraction",
                "Fraud detection optimization",
                "File upload method for efficiency"
            ]
        }

    def update_vision_model(self, new_model: str) -> None:
        """Update the vision model used for document extraction."""
        try:
            # Test the new model with a simple text message
            test_response = self.client.chat.completions.create(
                model=new_model,
                messages=[
                    {
                        "role": "user",
                        "content": "Test message"
                    }
                ],
                max_tokens=10
            )

            # Update if successful
            self.vision_model_name = new_model

        except Exception as e:
            raise ValueError(f"Invalid vision model '{new_model}': {str(e)}")

    def update_summary_model(self, new_model: str) -> None:
        """Update the summary model used for document summarization."""
        try:
            # Test the new model with a simple message
            test_response = self.client.chat.completions.create(
                model=new_model,
                messages=[
                    {
                        "role": "user",
                        "content": "Test message"
                    }
                ],
                max_tokens=10
            )

            # Update if successful
            self.summary_model_name = new_model

        except Exception as e:
            raise ValueError(f"Invalid summary model '{new_model}': {str(e)}")
