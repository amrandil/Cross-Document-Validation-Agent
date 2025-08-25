"""API routes for fraud detection service."""

import uuid
import time
import json
import asyncio
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
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
from ..utils.logging_config import (
    log_step, log_document, log_performance, log_error,
    log_llm, log_agent, log_fraud, set_streaming_bundle_id,
    add_streaming_callback, remove_streaming_callback, logger
)

router = APIRouter()

# Store active streaming connections
active_streams: Dict[str, asyncio.Queue] = {}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    log_step("health_check", endpoint="/health")
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
    use_react_agent: bool = Query(False, description="Use the new ReAct agent instead of the fixed-phase agent"),
    executor: FraudDetectionExecutor = Depends(get_fraud_executor)
):
    """Analyze documents for fraud detection.

    This endpoint accepts a bundle of customs documents and performs
    comprehensive fraud analysis using either the fixed-phase agent or ReAct agent.
    """
    start_time = time.time()
    bundle_id = request.bundle_id or f"bundle_{uuid.uuid4().hex[:8]}"

    log_step("start", message="Document analysis request received",
             bundle_id=bundle_id, documents_count=len(request.documents), use_react_agent=use_react_agent)

    try:
        # Generate bundle ID if not provided
        bundle_id = request.bundle_id or f"bundle_{uuid.uuid4().hex[:8]}"

        if use_react_agent:
            # Use ReAct agent with extracted content
            extracted_content = {}
            for doc_data in request.documents:
                extracted_content[doc_data["filename"]] = doc_data["content"]
            
            # Execute ReAct analysis
            execution = executor.execute_react_fraud_analysis(extracted_content, request.options)
        else:
            # Use old fixed-phase agent with document bundle
            # Convert request documents to Document objects
            documents = []
            for i, doc_data in enumerate(request.documents):
                try:
                    document = Document(
                        document_type=DocumentType(doc_data["document_type"]),
                        filename=doc_data["filename"],
                        content=doc_data["content"],
                        metadata=doc_data.get("metadata", {})
                    )
                    documents.append(document)

                    # Log document processing
                    content_size = len(doc_data["content"])
                    log_document(
                        doc_type=doc_data["document_type"],
                        file_size=f"{content_size:,} chars",
                        pages=doc_data.get("metadata", {}).get("pages", 1),
                        filename=doc_data["filename"],
                        bundle_id=bundle_id
                    )

                except ValueError as e:
                    log_error("validation_error", f"Invalid document type: {doc_data.get('document_type')}",
                              bundle_id=bundle_id, error=str(e))
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid document type: {doc_data.get('document_type')}. {str(e)}"
                    )

            log_step("complete", message="Documents processed",
                     bundle_id=bundle_id, documents_count=len(documents))

            # Create document bundle
            bundle = DocumentBundle(
                bundle_id=bundle_id,
                documents=documents
            )

            # Execute analysis using old agent
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
            documents_processed=len(request.documents)
        )

        log_step("complete", message="Analysis completed",
                 bundle_id=bundle_id, processing_time=processing_time, use_react_agent=use_react_agent)
        return response

    except AgentExecutionError as e:
        log_error("agent_execution_error", f"Agent execution error: {str(e)}",
                  bundle_id=bundle_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )

    except DocumentProcessingError as e:
        log_error("document_processing_error", f"Document processing error: {str(e)}",
                  bundle_id=bundle_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document processing failed: {str(e)}"
        )

    except FraudDetectionError as e:
        log_error("fraud_detection_error", f"Fraud detection error: {str(e)}",
                  bundle_id=bundle_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fraud detection failed: {str(e)}"
        )

    except Exception as e:
        log_error("unexpected_error", f"Unexpected error in analysis: {str(e)}",
                  bundle_id=bundle_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/analyze/react", response_model=AnalysisResponse)
async def analyze_documents_react(
    extracted_content: Dict[str, str],
    options: Dict[str, Any] = None,
    executor: FraudDetectionExecutor = Depends(get_fraud_executor)
):
    """Analyze extracted document content using the ReAct agent.

    This endpoint accepts extracted text content from documents and performs
    fraud analysis using the new ReAct agent.
    """
    start_time = time.time()
    bundle_id = f"bundle_{uuid.uuid4().hex[:8]}"

    log_step("start", message="ReAct analysis request received",
             bundle_id=bundle_id, documents_count=len(extracted_content))

    try:
        # Execute ReAct analysis
        execution = executor.execute_react_fraud_analysis(extracted_content, options)

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
            documents_processed=len(extracted_content)
        )

        log_step("complete", message="ReAct analysis completed",
                 bundle_id=bundle_id, processing_time=processing_time)
        return response

    except AgentExecutionError as e:
        log_error("react_agent_execution_error", f"ReAct agent execution error: {str(e)}",
                  bundle_id=bundle_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ReAct agent execution failed: {str(e)}"
        )

    except Exception as e:
        log_error("react_unexpected_error", f"Unexpected error in ReAct analysis: {str(e)}",
                  bundle_id=bundle_id, error=str(e))
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

        log_step("start", message="File upload analysis request received",
                 bundle_id=bundle_id, files_count=len(files))

        # Initialize vision PDF processor
        vision_processor = VisionPDFProcessor.get_instance()

        # Process uploaded files
        documents = []
        for i, file in enumerate(files):
            try:
                # Log file upload
                filename = file.filename or "unknown"
                log_step("upload", message=f"Processing file {i+1}/{len(files)}",
                         filename=filename, bundle_id=bundle_id)

                # Read file content
                content = await file.read()
                file_size = len(content)
                log_step("preprocess", message="File content read",
                         filename=filename, size=f"{file_size:,} bytes", bundle_id=bundle_id)

                # Determine document type from filename first (needed for vision processing)
                doc_type = _determine_document_type(filename)
                log_step("preprocess", message="Document type determined",
                         filename=filename, doc_type=doc_type, bundle_id=bundle_id)

                # Handle different file types
                if filename.lower().endswith('.pdf') or VisionPDFProcessor.is_pdf(content):
                    log_step("preprocess", message="Processing PDF with vision LLM",
                             filename=filename, bundle_id=bundle_id)

                    # Extract comprehensive content using vision LLM
                    content_str = vision_processor.extract_comprehensive_content(
                        pdf_bytes=content,
                        filename=filename,
                        document_type=doc_type
                    )

                    log_step("preprocess", message="PDF content extracted",
                             filename=filename, content_length=f"{len(content_str):,} chars", bundle_id=bundle_id)
                else:
                    log_step("preprocess", message="Processing text file",
                             filename=filename, bundle_id=bundle_id)

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
                                log_step("preprocess", message=f"File decoded with {encoding}",
                                         filename=filename, bundle_id=bundle_id)
                                break
                            except UnicodeDecodeError:
                                continue

                        if content_str is None:
                            log_error("encoding_error", f"Could not decode file {filename}",
                                      bundle_id=bundle_id, filename=filename)
                            raise ValueError(
                                f"Could not decode file {filename} - unsupported encoding or binary format")

                document = Document(
                    document_type=doc_type,
                    filename=filename,
                    content=content_str
                )
                documents.append(document)

                # Log document creation
                log_document(
                    doc_type=doc_type,
                    file_size=f"{len(content_str):,} chars",
                    pages=1,  # Default for now
                    filename=filename,
                    bundle_id=bundle_id
                )

                log_step("complete", message=f"File {i+1} processed successfully",
                         filename=filename, bundle_id=bundle_id)

            except Exception as e:
                log_error("file_processing_error", f"Error processing file {file.filename}",
                          bundle_id=bundle_id, filename=file.filename, error=str(e))
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error processing file {file.filename}: {str(e)}"
                )

        if not documents:
            log_error("no_documents", "No valid documents provided",
                      bundle_id=bundle_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid documents provided"
            )

        log_step("complete", message="All files processed",
                 bundle_id=bundle_id, documents_count=len(documents))

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

        # Execute fraud analysis using ReAct agent
        log_step("start", message="Starting ReAct fraud analysis",
                 bundle_id=bundle_id)
        
        # Convert bundle to extracted content format for ReAct agent
        extracted_content = {}
        for doc in documents:
            extracted_content[doc.filename] = doc.content
        
        execution = executor.execute_react_fraud_analysis(extracted_content, options_dict)

        # Calculate processing time
        processing_time = time.time() - start_time
        log_performance("total_analysis", processing_time, bundle_id=bundle_id)

        # Log fraud detection results
        if execution.fraud_analysis:
            confidence = execution.fraud_analysis.confidence
            indicators = execution.fraud_analysis.indicators
            log_fraud(confidence, indicators, bundle_id=bundle_id)

        log_step("complete", message="Fraud analysis completed",
                 bundle_id=bundle_id, execution_id=execution.execution_id)

        # Create response
        response = AnalysisResponse(
            success=True,
            bundle_id=bundle_id,
            execution_id=execution.execution_id,
            agent_execution=execution,
            fraud_analysis=execution.fraud_analysis,
            processing_time_ms=int(processing_time * 1000),
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
    """Streaming endpoint for real-time document analysis with detailed preprocessing updates."""

    # Generate bundle ID if not provided
    if not bundle_id:
        bundle_id = f"bundle_{uuid.uuid4().hex[:8]}"

    # Set up streaming logging
    set_streaming_bundle_id(bundle_id)

    # Create a queue for streaming updates
    stream_queue = asyncio.Queue()

    async def stream_analysis():
        try:
            # Send initial connection message
            # Padding to defeat potential proxy/browser buffering thresholds
            yield f": {' ' * 2048}\n\n"
            yield f"retry: 2000\n\n"
            yield f"data: {json.dumps({'type': 'connection', 'bundle_id': bundle_id, 'message': 'Stream connected'})}\n\n"

            # Process files with detailed streaming updates
            vision_processor = VisionPDFProcessor.get_instance()
            documents = []
            start_pre = time.time()

            yield f"data: {json.dumps({'type': 'preprocessing_started', 'bundle_id': bundle_id, 'message': 'Preprocessing files...'})}\n\n"

            # Ensure initial messages are sent before any file processing
            await asyncio.sleep(0.1)

            for i, file in enumerate(files):
                content = await file.read()
                filename = file.filename or "unknown"
                doc_type = _determine_document_type(filename)

                # Announce file start
                yield f"data: {json.dumps({
                    'type': 'file_started',
                    'filename': filename,
                    'document_type': doc_type.value,
                    'file_number': i + 1,
                    'total_files': len(files),
                    'message': f'Starting to process {filename} ({i+1}/{len(files)})'
                })}\n\n"

                if filename.lower().endswith('.pdf') or VisionPDFProcessor.is_pdf(content):
                    # Set up streaming callback for this file
                    async def streaming_callback(update):
                        # Send preprocessing updates to the client via the stream queue
                        await stream_queue.put(update)

                    add_streaming_callback(streaming_callback)

                    try:
                        # Start PDF processing in background while monitoring the queue
                        processing_task = asyncio.create_task(
                            vision_processor.extract_comprehensive_content_async(
                                content,
                                filename,
                                doc_type
                            )
                        )

                        # Monitor the queue and process updates in real-time
                        while not processing_task.done():
                            try:
                                # Process any available updates with a short timeout
                                update = await asyncio.wait_for(stream_queue.get(), timeout=0.05)
                                yield f"data: {json.dumps(update)}\n\n"
                            except asyncio.TimeoutError:
                                # No update available, continue monitoring
                                continue
                            except asyncio.QueueEmpty:
                                # Queue is empty, continue monitoring
                                continue

                        # Get the result from the processing task
                        content_str = await processing_task

                        # Process any remaining updates in the queue
                        while not stream_queue.empty():
                            try:
                                update = stream_queue.get_nowait()
                                yield f"data: {json.dumps(update)}\n\n"
                            except asyncio.QueueEmpty:
                                break

                        # Send extracted content update after processing is complete
                        yield f"data: {json.dumps({
                            'type': 'extracted_content',
                            'filename': filename,
                            'document_type': doc_type.value,
                            'content': content_str,
                            'content_length': f"{len(content_str):,} chars",
                            'message': f'Content extracted from {filename}'
                        })}\n\n"

                    except Exception as e:
                        yield f"data: {json.dumps({
                            'type': 'file_error',
                            'filename': filename,
                            'message': f'Failed to extract {filename}: {str(e)}'
                        })}\n\n"
                        raise
                    finally:
                        remove_streaming_callback(streaming_callback)
                else:
                    # Handle text files
                    yield f"data: {json.dumps({
                        'type': 'preprocessing_step',
                        'step': 'processing_text_file',
                        'filename': filename,
                        'message': f'Processing text file {filename}'
                    })}\n\n"

                    try:
                        content_str = content.decode('utf-8')
                    except UnicodeDecodeError:
                        encodings = ['latin1', 'cp1252', 'iso-8859-1']
                        content_str = None
                        for encoding in encodings:
                            try:
                                content_str = content.decode(encoding)
                                yield f"data: {json.dumps({
                                    'type': 'preprocessing_step',
                                    'step': 'file_decoded',
                                    'filename': filename,
                                    'encoding': encoding,
                                    'message': f'File decoded with {encoding}'
                                })}\n\n"
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
                yield f"data: {json.dumps({
                    'type': 'file_completed',
                    'filename': filename,
                    'file_number': i + 1,
                    'total_files': len(files),
                    'message': f'Completed processing {filename} ({i+1}/{len(files)})'
                })}\n\n"

            # Create bundle
            bundle = DocumentBundle(bundle_id=bundle_id, documents=documents)

            elapsed_pre = int((time.time() - start_pre) * 1000)
            yield f"data: {json.dumps({
                'type': 'preprocessing_completed',
                'bundle_id': bundle_id,
                'count': len(documents),
                'duration_ms': elapsed_pre,
                'message': f'Preprocessing complete - {len(documents)} files processed in {elapsed_pre/1000:.1f}s'
            })}\n\n"

            # Parse options
            try:
                options_dict = json.loads(options) if options else {}
            except json.JSONDecodeError:
                options_dict = {}

            # Convert bundle to extracted content format for ReAct agent
            extracted_content = {}
            for doc in documents:
                extracted_content[doc.filename] = doc.content
            
            # Start streaming analysis in background task using ReAct agent
            analysis_task = asyncio.create_task(
                executor.execute_react_fraud_analysis_stream(
                    extracted_content, options_dict, stream_queue)
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
            yield f"data: {json.dumps({'type': 'stream_error', 'error': error_msg})}\n\n"
            log_error("stream_error", error_msg, bundle_id=bundle_id)

    return StreamingResponse(
        stream_analysis(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
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
