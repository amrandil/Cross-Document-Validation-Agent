"""API routes for fraud detection service."""

import uuid
import time
import json
import asyncio
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.background import BackgroundTasks
from datetime import datetime

from .dependencies import get_fraud_executor
from ..agent.executor import FraudDetectionExecutor
from ..models.api import AnalysisRequest, AnalysisResponse, HealthResponse, ErrorResponse
from ..models.documents import DocumentBundle, Document, DocumentType
from ..config import settings
from ..utils.exceptions import FraudDetectionError, DocumentProcessingError, AgentExecutionError
from ..utils.vision_pdf_processor import VisionPDFProcessor

router = APIRouter()

# Store active streaming connections
active_streams: Dict[str, asyncio.Queue] = {}


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

        return response

    except AgentExecutionError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )

    except DocumentProcessingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document processing failed: {str(e)}"
        )

    except FraudDetectionError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fraud detection failed: {str(e)}"
        )

    except Exception as e:
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

        # Initialize vision PDF processor
        vision_processor = VisionPDFProcessor.get_instance()

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

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/analyze/stream")
async def analyze_documents_stream(
    files: List[UploadFile] = File(...),
    bundle_id: str = Form(None),
    options: str = Form("{}"),
    executor: FraudDetectionExecutor = Depends(get_fraud_executor)
):
    """Stream real-time fraud analysis updates using Server-Sent Events."""

    if not bundle_id:
        bundle_id = f"bundle_{uuid.uuid4().hex[:8]}"

    # Create a queue for this stream
    stream_queue = asyncio.Queue()
    active_streams[bundle_id] = stream_queue

    async def stream_analysis():
        try:
            # Send initial connection message
            # Padding to defeat potential proxy/browser buffering thresholds
            yield f": {' ' * 2048}\n\n"
            yield f"retry: 2000\n\n"
            yield f"data: {json.dumps({'type': 'connection', 'bundle_id': bundle_id, 'message': 'Stream connected'})}\n\n"

            # Process files (same as upload endpoint)
            vision_processor = VisionPDFProcessor.get_instance()
            documents = []
            start_pre = time.time()

            yield f"data: {json.dumps({'type': 'preprocessing_started', 'bundle_id': bundle_id, 'message': 'Preprocessing files...'})}\n\n"

            for file in files:
                content = await file.read()
                filename = file.filename or "unknown"
                doc_type = _determine_document_type(filename)

                # Announce file start
                yield f"data: {json.dumps({'type': 'file_started', 'filename': filename, 'document_type': doc_type.value, 'message': f'Starting to process {filename}'})}\n\n"

                if filename.lower().endswith('.pdf') or VisionPDFProcessor.is_pdf(content):
                    # Run potentially slow PDF processing without blocking event loop
                    try:
                        content_str = await asyncio.to_thread(
                            vision_processor.extract_comprehensive_content,
                            content,
                            filename,
                            doc_type
                        )
                    except Exception as e:
                        yield f"data: {json.dumps({'type': 'file_error', 'filename': filename, 'message': f'Failed to extract {filename}: {str(e)}'})}\n\n"
                        raise
                else:
                    try:
                        content_str = content.decode('utf-8')
                    except UnicodeDecodeError:
                        encodings = ['latin1', 'cp1252', 'iso-8859-1']
                        content_str = None
                        for encoding in encodings:
                            try:
                                content_str = content.decode(encoding)
                                break
                            except UnicodeDecodeError:
                                continue
                        if content_str is None:
                            raise ValueError(
                                f"Could not decode file {filename}")

                document = Document(
                    document_type=doc_type,
                    filename=filename,
                    content=content_str
                )
                documents.append(document)

                # Announce file completion
                yield f"data: {json.dumps({'type': 'file_completed', 'filename': filename, 'message': f'Completed processing {filename}'})}\n\n"

            # Create bundle
            bundle = DocumentBundle(bundle_id=bundle_id, documents=documents)

            elapsed_pre = int((time.time() - start_pre) * 1000)
            yield f"data: {json.dumps({'type': 'preprocessing_completed', 'bundle_id': bundle_id, 'count': len(documents), 'message': 'Preprocessing complete'})}\n\n"

            # Parse options
            try:
                options_dict = json.loads(options) if options else {}
            except json.JSONDecodeError:
                options_dict = {}

            # Start streaming analysis in background task
            analysis_task = asyncio.create_task(
                executor.execute_fraud_analysis_stream(
                    bundle, options_dict, stream_queue)
            )

            # Consume queue and yield updates in real-time
            while True:
                try:
                    # Wait for updates with shorter timeout so keepalives flow frequently
                    update = await asyncio.wait_for(stream_queue.get(), timeout=5.0)

                    # Yield the update to the client
                    yield f"data: {json.dumps(update)}\n\n"

                    # Check if analysis is complete
                    if update.get('type') in ['analysis_completed', 'analysis_error']:
                        break

                except asyncio.TimeoutError:
                    # Send keep-alive (comment line per SSE spec)
                    yield f": keepalive {datetime.utcnow().isoformat()}\n\n"
                except Exception as e:
                    break

            # Wait for analysis task to complete
            try:
                await analysis_task
            except Exception as e:
                pass

        except Exception as e:
            error_msg = f"Streaming analysis failed: {str(e)}"
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
        finally:
            # Clean up
            if bundle_id in active_streams:
                del active_streams[bundle_id]
            yield f"data: {json.dumps({'type': 'complete', 'message': 'Analysis complete'})}\n\n"

    return StreamingResponse(
        stream_analysis(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


@router.get("/stream/{bundle_id}/status")
async def get_stream_status(bundle_id: str):
    """Get the status of a streaming analysis."""
    is_active = bundle_id in active_streams
    return {
        "bundle_id": bundle_id,
        "active": is_active,
        "timestamp": time.time()
    }


@router.get("/agent/info")
async def get_agent_info(executor: FraudDetectionExecutor = Depends(get_fraud_executor)):
    """Get information about the fraud detection agent."""
    try:
        info = executor.get_agent_info()
        return JSONResponse(content=info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting agent information: {str(e)}"
        )


@router.post("/agent/models")
async def update_agent_models(
    model_configs: Dict[str, str],
    executor: FraudDetectionExecutor = Depends(get_fraud_executor)
):
    """Update the language models used by the agent."""
    try:
        # Validate and update models
        result = await executor.update_models(model_configs)
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid model configuration: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating agent models: {str(e)}"
        )


@router.get("/processor/info")
async def get_processor_info():
    """Get information about the vision PDF processor."""
    try:
        processor = VisionPDFProcessor.get_instance()
        info = processor.get_processor_info()
        return JSONResponse(content=info)
    except Exception as e:
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
