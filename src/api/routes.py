"""API routes for fraud detection service."""

import uuid
import time
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse

from .dependencies import get_fraud_executor
from ..agent.executor import FraudDetectionExecutor
from ..models.api import AnalysisRequest, AnalysisResponse, HealthResponse, ErrorResponse
from ..models.documents import DocumentBundle, Document, DocumentType
from ..config import settings
from ..utils.logging import get_logger
from ..utils.exceptions import FraudDetectionError, DocumentProcessingError, AgentExecutionError
from ..utils.vision_pdf_processor import VisionPDFProcessor

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        uptime_seconds=0.0,  # Simplified for MVP
        environment=settings.environment,
        dependencies={"openai": "connected"}
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_documents(
    request: AnalysisRequest,
    executor: FraudDetectionExecutor = Depends(get_fraud_executor)
):
    """Analyze documents for fraud detection.

    This endpoint accepts a bundle of customs documents and performs
    comprehensive fraud analysis using the ReAct agent.
    """
    start_time = time.time()

    try:
        logger.info(
            f"Received analysis request for bundle: {request.bundle_id}")

        # Generate bundle ID if not provided
        bundle_id = request.bundle_id or f"bundle_{uuid.uuid4().hex[:8]}"

        # Convert request documents to Document objects
        documents = []
        for doc_data in request.documents:
            try:
                document = Document(
                    document_type=DocumentType(doc_data["document_type"]),
                    filename=doc_data["filename"],
                    content=doc_data["content"],
                    metadata=doc_data.get("metadata", {})
                )
                documents.append(document)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid document type: {doc_data.get('document_type')}. {str(e)}"
                )

        # Create document bundle
        bundle = DocumentBundle(
            bundle_id=bundle_id,
            documents=documents
        )

        # Execute fraud analysis
        execution = executor.execute_fraud_analysis(bundle, request.options)

        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)

        # Create response
        response = AnalysisResponse(
            success=True,
            bundle_id=bundle_id,
            execution_id=execution.execution_id,
            agent_execution=execution,
            fraud_analysis=execution.fraud_analysis,
            processing_time_ms=processing_time,
            documents_processed=len(documents)
        )

        logger.info(
            f"Analysis completed for bundle {bundle_id} in {processing_time}ms")
        return response

    except AgentExecutionError as e:
        logger.error(f"Agent execution error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )

    except DocumentProcessingError as e:
        logger.error(f"Document processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document processing failed: {str(e)}"
        )

    except FraudDetectionError as e:
        logger.error(f"Fraud detection error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fraud detection failed: {str(e)}"
        )

    except Exception as e:
        logger.error(f"Unexpected error in analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/analyze/upload", response_model=AnalysisResponse)
async def analyze_uploaded_documents(
    files: List[UploadFile] = File(...),
    bundle_id: str = Form(None),
    options: str = Form("{}"),
    executor: FraudDetectionExecutor = Depends(get_fraud_executor)
):
    """Analyze uploaded document files for fraud detection.

    This endpoint accepts file uploads and performs fraud analysis.
    Useful for the Streamlit frontend.
    """
    start_time = time.time()

    try:
        # Generate bundle ID if not provided
        if not bundle_id:
            bundle_id = f"bundle_{uuid.uuid4().hex[:8]}"

        logger.info(
            f"Received file upload analysis request for bundle: {bundle_id}")

        # Initialize vision PDF processor
        vision_processor = VisionPDFProcessor()

        # Process uploaded files
        documents = []
        for file in files:
            try:
                # Read file content
                content = await file.read()
                filename = file.filename or "unknown"

                # Determine document type from filename first (needed for vision processing)
                doc_type = _determine_document_type(filename)

                # Handle different file types
                if filename.lower().endswith('.pdf') or VisionPDFProcessor.is_pdf(content):
                    logger.info(f"Processing PDF with vision LLM: {filename}")
                    # Extract comprehensive content using vision LLM
                    content_str = vision_processor.extract_comprehensive_content(
                        pdf_bytes=content,
                        filename=filename,
                        document_type=doc_type
                    )
                else:
                    # Try to decode as text file
                    try:
                        content_str = content.decode('utf-8')
                    except UnicodeDecodeError:
                        # Try other common encodings
                        encodings = ['latin1', 'cp1252', 'iso-8859-1']
                        content_str = None
                        for encoding in encodings:
                            try:
                                content_str = content.decode(encoding)
                                logger.info(
                                    f"Successfully decoded {filename} using {encoding} encoding")
                                break
                            except UnicodeDecodeError:
                                continue

                        if content_str is None:
                            raise ValueError(
                                f"Could not decode file {filename} - unsupported encoding or binary format")

                document = Document(
                    document_type=doc_type,
                    filename=filename,
                    content=content_str
                )
                documents.append(document)

            except Exception as e:
                logger.error(
                    f"Error processing file {file.filename}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error processing file {file.filename}: {str(e)}"
                )

        if not documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid documents provided"
            )

        # Create document bundle
        bundle = DocumentBundle(
            bundle_id=bundle_id,
            documents=documents
        )

        # Parse options
        try:
            import json
            options_dict = json.loads(options) if options else {}
        except json.JSONDecodeError:
            options_dict = {}

        # Execute fraud analysis
        execution = executor.execute_fraud_analysis(bundle, options_dict)

        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)

        # Create response
        response = AnalysisResponse(
            success=True,
            bundle_id=bundle_id,
            execution_id=execution.execution_id,
            agent_execution=execution,
            fraud_analysis=execution.fraud_analysis,
            processing_time_ms=processing_time,
            documents_processed=len(documents)
        )

        logger.info(
            f"File upload analysis completed for bundle {bundle_id} in {processing_time}ms")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in file upload analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/agent/info")
async def get_agent_info(executor: FraudDetectionExecutor = Depends(get_fraud_executor)):
    """Get information about the fraud detection agent."""
    try:
        info = executor.get_agent_info()
        return JSONResponse(content=info)
    except Exception as e:
        logger.error(f"Error getting agent info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting agent information: {str(e)}"
        )


@router.get("/processor/info")
async def get_processor_info():
    """Get information about the vision PDF processor."""
    try:
        processor = VisionPDFProcessor()
        info = processor.get_processor_info()
        return JSONResponse(content=info)
    except Exception as e:
        logger.error(f"Error getting processor info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting processor information: {str(e)}"
        )


def _determine_document_type(filename: str) -> DocumentType:
    """Determine document type from filename."""
    filename_lower = filename.lower()

    if "invoice" in filename_lower:
        return DocumentType.COMMERCIAL_INVOICE
    elif "packing" in filename_lower or "pack" in filename_lower:
        return DocumentType.PACKING_LIST
    elif "bill" in filename_lower and "lading" in filename_lower:
        return DocumentType.BILL_OF_LADING
    elif "origin" in filename_lower or "certificate" in filename_lower:
        return DocumentType.CERTIFICATE_OF_ORIGIN
    elif "customs" in filename_lower or "declaration" in filename_lower:
        return DocumentType.CUSTOMS_DECLARATION
    else:
        # Default to commercial invoice for unknown types
        return DocumentType.COMMERCIAL_INVOICE
