"""
FastAPI Application for Real Estate RAG System
Endpoints:
- POST /ingest - Ingest all PDFs from PDF_UPLOAD_DIR
- POST /ingest/pdf - Ingest single PDF document
- POST /query/rag - Direct RAG query
- POST /query/agent - Query specific agent
- POST /query/auto - Auto-route to appropriate agent
- GET /health - Health check
- GET /stats - Collection statistics
"""
import logging
import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config.settings import settings
from models.schemas import (
    RAGQueryRequest,
    AgentRequest,
    PropertySearchRequest,
    AgentResponse,
    RAGResult,
    IngestionResponse
)
from services.milvus_service import get_milvus_service
from services.pdf_ingestion import get_pdf_ingestion_service
from orchestrator.agent_orchestrator import get_orchestrator
from agents.real_estate_agents import get_agent
from tools.property_tools import get_search_tool, get_rag_tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting Real Estate RAG System...")
    
    # Create directories
    os.makedirs(settings.PDF_UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.PDF_PROCESSED_DIR, exist_ok=True)
    
    # Connect to Milvus
    milvus_service = get_milvus_service()
    milvus_service.connect()
    
    # Create or load collection
    milvus_service.create_collection(drop_existing=False)
    
    logger.info("System initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    milvus_service.disconnect()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Real Estate Property Search and RAG System with Milvus",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Real Estate RAG System API",
        "version": settings.APP_VERSION,
        "endpoints": {
            "health": "/health",
            "stats": "/stats",
            "ingest_all": "/ingest",
            "ingest_pdf": "/ingest/pdf",
            "rag_query": "/query/rag",
            "agent_query": "/query/agent",
            "auto_route": "/query/auto",
            "search_properties": "/search/properties"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        milvus_service = get_milvus_service()
        stats = milvus_service.get_collection_stats()
        
        return {
            "status": "healthy",
            "milvus_connected": True,
            "collection": stats["collection_name"],
            "documents": stats["num_entities"]
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/stats")
async def get_stats():
    """Get collection statistics"""
    try:
        milvus_service = get_milvus_service()
        stats = milvus_service.get_collection_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest")
async def ingest_all_pdfs():
    """
    Ingest all PDFs from the configured PDF_UPLOAD_DIR into Milvus
    
    Returns:
        Summary of ingestion results
    """
    try:
        pdf_dir = settings.PDF_UPLOAD_DIR
        
        # Check if directory exists
        if not os.path.isdir(pdf_dir):
            raise HTTPException(
                status_code=400, 
                detail=f"PDF directory '{pdf_dir}' not found. Please create it and add PDF files."
            )
        
        # Get all PDF files
        pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            return {
                "status": "no_files",
                "message": f"No PDF files found in {pdf_dir}",
                "files_processed": 0
            }
        
        logger.info(f"Found {len(pdf_files)} PDF files to ingest")
        
        # Initialize services
        milvus_service = get_milvus_service()
        ingestion_service = get_pdf_ingestion_service()
        
        # Ensure collection exists
        milvus_service.create_collection(drop_existing=False)
        
        # Process each PDF
        results = []
        total_chunks = 0
        total_vectors = 0
        errors = []
        
        for pdf_file in pdf_files:
            file_path = os.path.join(pdf_dir, pdf_file)
            
            try:
                logger.info(f"Processing: {pdf_file}")
                result = ingestion_service.ingest_pdf(file_path, metadata={})
                
                if result["success"]:
                    total_chunks += result.get("chunks_created", 0)
                    total_vectors += result.get("vectors_inserted", 0)
                    results.append({
                        "file": pdf_file,
                        "status": "success",
                        "chunks": result.get("chunks_created", 0),
                        "vectors": result.get("vectors_inserted", 0)
                    })
                    
                    # Move to processed directory
                    processed_path = os.path.join(settings.PDF_PROCESSED_DIR, pdf_file)
                    os.rename(file_path, processed_path)
                    logger.info(f"Moved {pdf_file} to processed directory")
                else:
                    errors.append({
                        "file": pdf_file,
                        "error": result.get("error", "Unknown error")
                    })
                    
            except Exception as e:
                logger.error(f"Error processing {pdf_file}: {str(e)}")
                errors.append({
                    "file": pdf_file,
                    "error": str(e)
                })
        
        return {
            "status": "complete",
            "message": f"Processed {len(results)} PDFs successfully",
            "files_processed": len(results),
            "total_chunks_created": total_chunks,
            "total_vectors_inserted": total_vectors,
            "successful_files": results,
            "errors": errors if errors else None
        }
        
    except Exception as e:
        logger.error(f"Error in batch ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/pdf", response_model=IngestionResponse)
async def ingest_pdf(
    file: UploadFile = File(...),
    locality: Optional[str] = None,
    property_type: Optional[str] = None
):
    """
    Ingest PDF document into Milvus vector database
    
    Args:
        file: PDF file to ingest
        locality: Optional locality tag
        property_type: Optional property type tag
    
    Returns:
        Ingestion results
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save uploaded file
        file_path = os.path.join(settings.PDF_UPLOAD_DIR, file.filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Saved uploaded file: {file.filename}")
        
        # Prepare metadata
        metadata = {}
        if locality:
            metadata["locality"] = locality
        if property_type:
            metadata["property_type"] = property_type
        
        # Ingest PDF
        ingestion_service = get_pdf_ingestion_service()
        result = ingestion_service.ingest_pdf(file_path, metadata)
        
        # Move to processed directory
        if result["success"]:
            processed_path = os.path.join(settings.PDF_PROCESSED_DIR, file.filename)
            os.rename(file_path, processed_path)
            logger.info(f"Moved processed file to: {processed_path}")
        
        return IngestionResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in PDF ingestion endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/rag")
async def query_rag(request: RAGQueryRequest):
    """
    Direct RAG query endpoint
    Searches vector database and generates answer
    
    Args:
        request: RAG query request with query and conversation history
    
    Returns:
        Answer with retrieved context
    """
    try:
        rag_tool = get_rag_tool()
        
        # Build context from conversation history
        context_text = ""
        if request.conversation_history:
            # Use last N messages as specified in max_history
            recent_history = request.conversation_history[-request.max_history:]
            context_parts = []
            for msg in recent_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    context_parts.append(f"User: {content}")
                elif role == "assistant":
                    context_parts.append(f"Assistant: {content}")
            
            if context_parts:
                context_text = "\n".join(context_parts)
                logger.info(f"Using conversation context: {len(context_parts)} messages")
        
        # Enhance query with context if available
        enhanced_query = request.query
        if context_text:
            enhanced_query = f"""Previous conversation:
{context_text}

Current question: {request.query}

Please answer the current question, taking into account the conversation history above."""
        
        result = rag_tool.execute(
            query=enhanced_query,
            top_k=5
        )
        
        response_data = {
            "query": request.query,
            "answer": result["answer"],
            "retrieved_documents": [],
            "confidence_score": None
        }
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error in RAG query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/agent", response_model=AgentResponse)
async def query_agent(request: AgentRequest):
    """
    Query specific agent (buy, rent, or details)
    
    Args:
        request: Agent query request with conversation history
    
    Returns:
        Agent response
    """
    try:
        agent = get_agent(request.agent_type.value)
        
        # Add conversation history to context
        context = request.context or {}
        if request.conversation_history:
            context["conversation_history"] = request.conversation_history[-10:]  # Last 10 messages
        
        response = agent.process_message(request.message, context)
        
        return AgentResponse(**response)
        
    except Exception as e:
        logger.error(f"Error in agent query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/auto")
async def query_auto(request: RAGQueryRequest):
    """
    Auto-route query to appropriate agent or RAG
    Uses orchestrator for intelligent routing
    
    Args:
        request: Query with conversation history
    
    Returns:
        Response from appropriate agent or RAG
    """
    try:
        orchestrator = get_orchestrator()
        
        # Build context string from conversation history
        context_info = {}
        if request.conversation_history:
            context_info["conversation_history"] = request.conversation_history[-10:]
        
        response = orchestrator.route_query(request.query)
        
        # Add conversation context info to response
        if context_info:
            response["context_used"] = f"{len(context_info.get('conversation_history', []))} previous messages"
        
        return response
        
    except Exception as e:
        logger.error(f"Error in auto routing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/properties")
async def search_properties(request: PropertySearchRequest):
    """
    Search properties directly using search tool
    
    Args:
        request: Property search criteria
    
    Returns:
        List of matching properties
    """
    try:
        search_tool = get_search_tool()
        
        # Build search parameters
        search_params = {
            "transaction_type": "buy"  # default
        }
        
        if request.locality:
            search_params["locality"] = request.locality
        if request.property_type:
            search_params["property_type"] = request.property_type
        if request.min_price:
            search_params["min_price"] = request.min_price
        if request.max_price:
            search_params["max_price"] = request.max_price
        if request.bedrooms:
            search_params["bedrooms"] = request.bedrooms
        
        result = search_tool.execute(**search_params)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in property search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/reset-collection")
async def reset_collection():
    """
    Reset Milvus collection (delete and recreate)
    USE WITH CAUTION - This will delete all data
    """
    try:
        milvus_service = get_milvus_service()
        milvus_service.create_collection(drop_existing=True)
        
        return {
            "message": "Collection reset successfully",
            "collection_name": settings.MILVUS_COLLECTION_NAME
        }
        
    except Exception as e:
        logger.error(f"Error resetting collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
