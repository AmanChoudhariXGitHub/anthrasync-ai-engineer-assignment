"""
FastAPI backend for Enterprise Knowledge Assistant RAG system.
Provides REST endpoints for document management and question answering.
"""

import os
import logging
from typing import List
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile

from document_processor import DocumentProcessor
from vector_store import VectorStore
from llm_provider import GroqProvider, RAGChain
from evaluation import RAGEvaluator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Enterprise Knowledge Assistant",
    description="RAG-based Q&A system for enterprise documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
vector_store = None
rag_chain = None
evaluator = None

# Pydantic models
class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    question: str
    top_k: int = 5
    max_tokens: int = 512


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    status: str
    filename: str
    chunks: int
    message: str


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    question: str
    answer: str
    sources: List[dict]
    retrieval_count: int
    model: str


class CollectionInfo(BaseModel):
    """Response model for collection info."""
    total_chunks: int
    embedding_model: str
    status: str


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global vector_store, rag_chain, evaluator
    
    logger.info("Initializing RAG components...")
    
    # Initialize vector store
    persist_dir = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    vector_store = VectorStore(persist_dir=persist_dir, model_name=embedding_model)
    
    # Initialize LLM provider (using Groq API)
    groq_api_key = os.getenv("GROQ_API_KEY")
    groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    llm_provider = GroqProvider(api_key=groq_api_key, model=groq_model)
    
    # Initialize RAG chain
    rag_chain = RAGChain(vector_store, llm_provider)
    
    # Initialize evaluator
    evaluator = RAGEvaluator()
    
    logger.info("RAG components initialized successfully")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "vector_store": vector_store is not None,
        "rag_chain": rag_chain is not None
    }


@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document.
    
    Supports: PDF, DOCX, TXT files
    """
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    # Validate file extension
    allowed_extensions = {'.pdf', '.docx', '.txt'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: {allowed_extensions}"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Process document
        doc_data = DocumentProcessor.process_document(tmp_path)
        
        # Add to vector store
        vector_store.add_documents([doc_data])
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return DocumentUploadResponse(
            status="success",
            filename=doc_data["filename"],
            chunks=doc_data["chunk_count"],
            message=f"Successfully processed {doc_data['chunk_count']} chunks"
        )
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the knowledge base.
    
    Returns answer with sources and confidence scores.
    """
    if rag_chain is None:
        raise HTTPException(status_code=503, detail="RAG chain not initialized")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        result = rag_chain.query(
            request.question,
            top_k=request.top_k,
            max_tokens=request.max_tokens
        )
        
        return QueryResponse(
            question=result["question"],
            answer=result["answer"],
            sources=result["sources"],
            retrieval_count=result["retrieval_count"],
            model=result["model"]
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/collection-info", response_model=CollectionInfo)
async def get_collection_info():
    """Get information about the current collection."""
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    info = vector_store.get_collection_info()
    
    return CollectionInfo(
        total_chunks=info["total_chunks"],
        embedding_model=info["embedding_model"],
        status="ready"
    )


@app.delete("/collection")
async def clear_collection():
    """Clear all documents from the collection."""
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    result = vector_store.clear_collection()
    return result


@app.post("/evaluate")
async def evaluate_response(
    question: str = Query(...),
    reference_answer: str = Query(...),
    generated_answer: str = Query(...)
):
    """
    Evaluate a generated answer using multiple metrics.
    
    Returns BLEU, ROUGE, and token overlap scores.
    """
    if evaluator is None:
        raise HTTPException(status_code=503, detail="Evaluator not initialized")
    
    try:
        metrics = evaluator.evaluate_answer(question, reference_answer, generated_answer)
        return metrics
        
    except Exception as e:
        logger.error(f"Error evaluating response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with API documentation."""
    return {
        "name": "Enterprise Knowledge Assistant",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload": "/upload (POST)",
            "query": "/query (POST)",
            "collection_info": "/collection-info (GET)",
            "clear_collection": "/collection (DELETE)",
            "evaluate": "/evaluate (POST)"
        },
        "docs": "/docs"
    }


if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    uvicorn.run(app, host=host, port=port)
