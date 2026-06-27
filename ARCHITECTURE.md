# Architecture Document: Enterprise Knowledge Assistant

## Overview

The Enterprise Knowledge Assistant is a production-grade RAG (Retrieval-Augmented Generation) system that combines document retrieval with generative AI to provide accurate, source-attributed answers to enterprise questions.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                      │
├──────────────────────────────┬──────────────────────────────────┤
│   Streamlit Frontend         │     REST API (FastAPI)            │
│   ├─ Document Upload         │     ├─ POST /upload              │
│   ├─ Q&A Chat Interface      │     ├─ POST /query               │
│   ├─ Evaluation Dashboard    │     ├─ GET /health               │
│   └─ Collection Stats        │     ├─ DELETE /collection        │
│                              │     └─ POST /evaluate            │
└──────────────────────────────┴──────────────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
        ┌───────────▼──────────┐  ┌───▼──────────┐  ┌───▼────────────┐
        │  Document Processing │  │ Retrieval    │  │  Generation    │
        │      Layer           │  │   Layer      │  │     Layer      │
        └──────────────────────┘  └──────────────┘  └────────────────┘
                    │                  │                      │
        ┌───────────▼──────────┐  ┌───▼──────────┐  ┌───▼────────────┐
        │  Chunking & Text     │  │  Vector      │  │   Ollama LLM   │
        │  Extraction          │  │  Search      │  │   (Mistral)    │
        ├──────────────────────┤  │  (ChromaDB)  │  │                │
        │ • PDF Parser         │  │              │  │ • Mistral 7B   │
        │ • DOCX Extractor     │  │ • Cosine     │  │ • Prompt       │
        │ • TXT Handler        │  │   Similarity │  │   Synthesis    │
        │ • Sentence Breaker   │  │ • Top-K      │  │ • Token        │
        │ • Metadata Extractor │  │   Retrieval  │  │   Generation   │
        └──────────────────────┘  └──────────────┘  └────────────────┘
                    │                  │                      │
        ┌───────────▼──────────┐  ┌───▼──────────┐  ┌───▼────────────┐
        │  Text Processing     │  │  Embedding   │  │  Response      │
        │  (raw_text → chunks) │  │  Model       │  │  Formatting    │
        │                      │  │ (Sentence    │  │                │
        │  Output:             │  │  Transformers│  │  Output:       │
        │  - chunk_id          │  │              │  │  - answer      │
        │  - chunk_text        │  │  Output:     │  │  - confidence  │
        │  - metadata          │  │  - vector    │  │  - sources     │
        │  - source_file       │  │  - metadata  │  │  - model_name  │
        └──────────────────────┘  └──────────────┘  └────────────────┘
                    │                  │                      │
                    └──────────────────┴──────────────────────┘
                                       │
                            ┌──────────▼──────────┐
                            │  Evaluation Layer   │
                            ├─────────────────────┤
                            │ • BLEU Score        │
                            │ • ROUGE Metrics     │
                            │ • Token Overlap     │
                            │ • Retrieval F1      │
                            └─────────────────────┘
                                       │
                            ┌──────────▼──────────┐
                            │   Response to User  │
                            │  {answer, sources,  │
                            │   metrics}          │
                            └─────────────────────┘
```

## Component Details

### 1. User Interface Layer

#### 1.1 Streamlit Frontend (`rag_system/frontend/app.py`)

**Responsibilities**:
- Document upload interface
- Interactive Q&A chat
- Collection statistics display
- Evaluation dashboard
- Session state management

**Key Features**:
- Drag-and-drop file upload
- Real-time chat history
- Source attribution display
- Metric visualization
- Responsive design

**Dependencies**:
- streamlit: UI framework
- requests: HTTP communication
- datetime: Timestamp management

**State Management**:
```python
st.session_state:
  - chat_history: List[Dict] - conversation history
  - collection_info: Dict - knowledge base stats
  - api_available: bool - backend connection status
```

#### 1.2 REST API Layer (`rag_system/backend/main.py`)

**Responsibilities**:
- HTTP request handling
- Input validation with Pydantic
- Response formatting
- Error handling
- CORS configuration

**Endpoints**:
- `POST /upload` - Document ingestion
- `POST /query` - Q&A queries
- `GET /health` - Service health
- `GET /collection-info` - Statistics
- `DELETE /collection` - Data reset
- `POST /evaluate` - Answer evaluation

**Framework**: FastAPI 0.104+
**Server**: Uvicorn ASGI
**Port**: 8000 (configurable)

---

### 2. Document Processing Layer

#### 2.1 Document Processor (`rag_system/backend/document_processor.py`)

**Responsibility**: Transform raw documents into chunks suitable for embedding

**Process**:
```
Input File (PDF/DOCX/TXT)
    │
    ├─ Format Detection
    │
    ├─ Text Extraction
    │  ├─ PDF: PyPDF2.PdfReader
    │  ├─ DOCX: python-docx Document
    │  └─ TXT: Plain text read
    │
    ├─ Chunking
    │  ├─ Size: 500 characters
    │  ├─ Overlap: 100 characters
    │  └─ Boundary: Sentence-aware
    │
    └─ Output: List[str] - document chunks
```

**Key Methods**:
```python
extract_text(file_path)      # Format-agnostic extraction
chunk_text(text)             # Split into overlapping chunks
process_document(file_path)  # End-to-end processing
process_documents(directory) # Batch processing
```

**Configuration**:
```python
CHUNK_SIZE = 500        # Characters per chunk
OVERLAP = 100          # Overlap between chunks
MAX_FILE_SIZE = 100MB  # Upload limit
```

**Quality Checks**:
- Validates file format
- Handles encoding errors
- Filters empty chunks
- Preserves metadata

---

### 3. Retrieval Layer

#### 3.1 Vector Store (`rag_system/backend/vector_store.py`)

**Responsibility**: Manage semantic embeddings and similarity search

**Architecture**:
```
ChromaDB (Vector Database)
    │
    ├─ Collection: "documents"
    │  ├─ IDs: Unique chunk identifiers
    │  ├─ Embeddings: 384-dim vectors
    │  ├─ Metadatas: Chunk metadata
    │  └─ Documents: Original text
    │
    ├─ Embedding Model: all-MiniLM-L6-v2 (33M params)
    │  ├─ Input: Text chunks
    │  ├─ Output: 384-dimensional vectors
    │  └─ Metric: Cosine similarity
    │
    └─ Index: HNSW (Hierarchical Navigable Small World)
       └─ Enables fast approximate NN search
```

**Key Methods**:
```python
add_documents(documents)    # Vectorize and store chunks
search(query, top_k=5)      # Semantic similarity search
get_collection_info()       # Collection statistics
clear_collection()          # Reset database
```

**Performance Characteristics**:
- Embedding generation: ~100 docs/sec
- Search latency: <100ms for 10k chunks
- Memory: ~384 bytes per chunk
- Storage: ~4KB per 1000 chunks (compressed)

**Similarity Scoring**:
```python
# Cosine distance to similarity conversion
similarity = 1 - (distance / 2)

# Example: distance 0.2 → similarity 0.9
```

---

### 4. Generation Layer

#### 4.1 LLM Provider (`rag_system/backend/llm_provider.py`)

**Responsibility**: Generate answers using open-source LLMs

**Architecture**:
```
User Query
    │
    ├─ Retrieve Context (top-k chunks)
    │
    ├─ Format Prompt
    │  ├─ System message: "You are a helpful assistant..."
    │  ├─ Context: Concatenated documents
    │  └─ Question: User query
    │
    ├─ LLM Inference (Ollama)
    │  ├─ Model: Mistral 7B
    │  ├─ Temperature: 0.7 (controllable)
    │  ├─ Max tokens: 512 (default)
    │  └─ Format: Text generation
    │
    └─ Post-processing
       ├─ Clean output
       ├─ Extract sources
       └─ Calculate confidence
```

**OllamaProvider Class**:
```python
class OllamaProvider:
    base_url: str              # Ollama server URL
    model: str                 # Model name (mistral, llama2, etc.)
    api_endpoint: str          # API endpoint
    
    def generate(prompt, max_tokens, temperature)
    def _is_available() -> bool
    def _mock_response(prompt) -> str  # Fallback
```

**Prompt Engineering**:
```python
prompt = f"""You are a helpful assistant answering questions based on provided documents.
        
CONTEXT:
[Document 1] (from {filename}, relevance: 0.89)
{chunk_text}

[Document 2] (from {filename}, relevance: 0.76)
{chunk_text}

Question: {question}

Answer based on the context provided above. If the answer is not in the context, say so."""
```

**Model Selection Trade-offs**:

| Model | Params | Speed | Quality | VRAM |
|-------|--------|-------|---------|------|
| orca-mini | 3B | Fast | Fair | 2GB |
| mistral | 7B | Medium | Good | 4GB |
| llama2 | 7B | Medium | Good | 4GB |
| neural-chat | 7B | Medium | Good | 4GB |

#### 4.2 RAG Chain (`rag_system/backend/llm_provider.py::RAGChain`)

**Responsibility**: Orchestrate retrieval and generation

**Process**:
```python
def query(question, top_k=5, max_tokens=512):
    # 1. Retrieve
    search_results = vector_store.search(question, top_k)
    
    # 2. Format context
    context = _format_context(search_results)
    
    # 3. Create prompt
    prompt = f"{context}\n\nQuestion: {question}\n\nAnswer:"
    
    # 4. Generate
    answer = llm_provider.generate(prompt, max_tokens)
    
    # 5. Extract sources
    sources = [
        {
            "filename": result["metadata"]["filename"],
            "relevance": result["similarity_score"],
            "chunk_id": result["metadata"]["chunk_id"]
        }
        for result in search_results
    ]
    
    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "retrieval_count": len(search_results),
        "model": llm_provider.model
    }
```

---

### 5. Evaluation Layer

#### 5.1 Evaluator (`rag_system/backend/evaluation.py`)

**Responsibility**: Compute quality metrics

**Metrics Implemented**:

1. **BLEU Score**
   - N-gram precision with brevity penalty
   - Range: 0-1 (higher better)
   - Good for: Lexical similarity

2. **ROUGE Score**
   - ROUGE-1: Unigram overlap
   - ROUGE-L: Longest common subsequence
   - Range: 0-1 (higher better)
   - Good for: Summary quality

3. **Token Overlap**
   - Jaccard Similarity: |A∩B|/|A∪B|
   - Token Precision/Recall
   - Range: 0-1 (higher better)
   - Good for: Content coverage

4. **Retrieval Metrics**
   - Precision: true_positives / (true_positives + false_positives)
   - Recall: true_positives / (true_positives + false_negatives)
   - F1: Harmonic mean
   - MRR: Mean Reciprocal Rank

**Implementation**:
```python
class RAGEvaluator:
    def calculate_bleu(reference, hypothesis) -> float
    def calculate_rouge(reference, hypothesis) -> Dict[str, float]
    def calculate_token_overlap(reference, hypothesis) -> Dict[str, float]
    def evaluate_answer(question, ref, gen) -> Dict
    def evaluate_retrieval(retrieved, relevant) -> Dict
```

---

## Data Flow Sequences

### Sequence 1: Document Upload and Indexing

```
User
  │
  └─► Streamlit UI (Upload)
      │
      └─► FastAPI /upload endpoint
          │
          ├─► Save temp file
          │
          ├─► DocumentProcessor.process_document()
          │   ├─► Extract text
          │   ├─► Chunk text
          │   └─► Generate metadata
          │
          ├─► VectorStore.add_documents()
          │   ├─► SentenceTransformer.encode()
          │   │   └─► Generate embeddings
          │   │
          │   └─► ChromaDB.add()
          │       └─► Store vectors + metadata
          │
          ├─► Delete temp file
          │
          └─► Return success response
              │
              └─► Streamlit displays "✅ Upload successful"
```

### Sequence 2: Question Answering

```
User (Input: "What is X?")
  │
  └─► Streamlit UI (/ask)
      │
      └─► FastAPI /query endpoint
          │
          ├─► VectorStore.search(question)
          │   ├─► SentenceTransformer.encode(question)
          │   │   └─► Generate query embedding
          │   │
          │   └─► ChromaDB.query()
          │       └─► Cosine similarity search → top-5 chunks
          │
          ├─► RAGChain.query()
          │   │
          │   ├─► Format context from chunks
          │   │
          │   ├─► Create prompt with context + question
          │   │
          │   └─► OllamaProvider.generate(prompt)
          │       ├─► Call Ollama API
          │       ├─► Wait for LLM inference
          │       └─► Get generated text
          │
          ├─► Extract sources from retrieved chunks
          │
          └─► Return response
              │
              ├─── Answer
              ├─── Source documents
              ├─── Relevance scores
              │
              └─► Streamlit displays results with formatting
                  └─► Add to chat history
```

### Sequence 3: Evaluation

```
User (Provides: question, reference, generated)
  │
  └─► Streamlit UI (/evaluate)
      │
      └─► FastAPI /evaluate endpoint
          │
          ├─► RAGEvaluator.evaluate_answer()
          │   │
          │   ├─► calculate_bleu()
          │   │   ├─► Tokenize both answers
          │   │   └─► Compute n-gram overlap
          │   │
          │   ├─► calculate_rouge()
          │   │   ├─► Get ROUGE-1 scores
          │   │   └─► Get ROUGE-L scores
          │   │
          │   └─► calculate_token_overlap()
          │       ├─► Compute Jaccard similarity
          │       └─► Compute precision/recall
          │
          └─► Return metrics
              │
              └─► Streamlit displays scores + interpretation
                  └─── BLEU: 0.85 (Good)
                  └─── ROUGE-1 F1: 0.82
                  └─── Jaccard: 0.75
```

---

## Data Models and Schemas

### Document Chunk Schema
```python
{
  "id": "document.pdf_0",
  "embedding": [0.12, -0.45, ..., 0.89],  # 384-dim vector
  "text": "Document content chunk...",
  "metadata": {
    "filename": "document.pdf",
    "format": "pdf",
    "chunk_id": 0,
    "total_chunks": 42,
    "upload_date": "2024-06-27"
  }
}
```

### Query Response Schema
```python
{
  "question": "What is X?",
  "answer": "Based on the documents... [LLM generated]",
  "sources": [
    {
      "filename": "doc1.pdf",
      "relevance": 0.92,
      "chunk_id": 5
    }
  ],
  "retrieval_count": 3,
  "model": "mistral"
}
```

### Evaluation Metrics Schema
```python
{
  "question": "What?",
  "bleu_score": 0.85,
  "rouge_scores": {
    "rouge1_precision": 0.88,
    "rouge1_recall": 0.82,
    "rouge1_fmeasure": 0.85,
    "rougeL_precision": 0.85,
    "rougeL_recall": 0.80,
    "rougeL_fmeasure": 0.82
  },
  "token_overlap": {
    "jaccard_similarity": 0.78,
    "token_precision": 0.82,
    "token_recall": 0.75
  }
}
```

---

## Performance Characteristics

### Latency Breakdown

```
Query Latency (typical):
├─ Embedding generation: 100ms (Sentence Transformer)
├─ Vector search: 50ms (ChromaDB cosine similarity)
├─ Context formatting: 50ms (Python processing)
├─ LLM inference: 15,000ms (Ollama + Mistral)
├─ Response formatting: 50ms (JSON serialization)
└─ Total: ~15.2 seconds
```

### Throughput

```
Single Machine Capacity:
├─ Concurrent queries: ~10
├─ Documents supported: ~10,000
├─ Total chunks: ~100,000
├─ Vector store size: ~400MB
└─ Memory requirement: 4GB
```

### Scaling Strategy

```
Single Server
  └─ FastAPI instances: 1
  └─ Worker processes: 1
  └─ Queries/sec: ~1

Production Cluster
  ├─ Load Balancer: Nginx
  ├─ FastAPI replicas: 4
  ├─ Worker processes: 16
  ├─ Vector store: Distributed ChromaDB server
  ├─ LLM inference: GPU cluster (8+ GPUs)
  └─ Queries/sec: ~50+
```

---

## Security Architecture

### Authentication (Recommended)
```python
from fastapi.security import OAuth2PasswordBearer, Depends

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/query")
async def query(request: QueryRequest, token: str = Depends(oauth2_scheme)):
    # Verify token
    user = verify_token(token)
    # Process query
```

### Input Validation
- Pydantic models validate all inputs
- File type and size restrictions
- Query length limits
- Rate limiting (optional)

### Data Security
- TLS/SSL for transport
- Encryption at rest for sensitive data
- Audit logging for compliance
- GDPR-compliant data handling

---

## Deployment Topology

### Development
```
Local Machine
├─ Python venv (isolated)
├─ Ollama (local, port 11434)
├─ FastAPI (localhost:8000)
├─ Streamlit (localhost:8501)
└─ ChromaDB (./chroma_db)
```

### Production
```
Cloud Infrastructure
├─ Kubernetes Cluster
│  ├─ FastAPI Pods (4 replicas)
│  ├─ Streamlit Pods (2 replicas)
│  ├─ ChromaDB StatefulSet
│  └─ Ollama Deployment (GPU nodes)
├─ Load Balancer (nginx/traefik)
├─ PostgreSQL (metadata storage)
├─ Redis (caching layer)
├─ S3 (document storage)
└─ Monitoring (Prometheus + Grafana)
```

---

## Monitoring and Observability

### Key Metrics
```
Application:
  - API response time (p50, p95, p99)
  - Queries per minute
  - Error rate
  - Cache hit rate

Model:
  - Embedding generation speed
  - LLM inference latency
  - Token generation rate
  - Memory usage

System:
  - CPU utilization
  - Memory usage
  - Disk space (vector store)
  - Network bandwidth
```

### Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rag_system.log'),
        logging.StreamHandler()
    ]
)
```

---

## Future Architecture Enhancements

### Phase 2
- Multi-turn conversation memory
- Query rewriting for complex questions
- Hybrid search (BM25 + semantic)
- Document summarization

### Phase 3
- Fine-tuning on enterprise data
- Multi-modal support (images, tables)
- Distributed vector store
- Real-time document updates

### Phase 4
- Federated learning for privacy
- Knowledge graph integration
- Advanced reasoning capabilities
- Custom model training pipeline

---

## Technology Justification

| Component | Choice | Justification |
|-----------|--------|---------------|
| **Backend** | FastAPI | Async, type-safe, auto-docs, high performance |
| **Frontend** | Streamlit | Rapid dev, data focus, easy deployment |
| **Vector DB** | ChromaDB | Lightweight, embedded, persistent, fast |
| **Embeddings** | Sentence Transformers | Semantic-aware, multilingual, efficient |
| **LLM** | Ollama (Mistral) | Open-source, local, privacy, cost-effective |
| **Document Parsing** | PyPDF2 + python-docx | Lightweight, Python-native, reliable |

---

**Document Version**: 1.0  
**Last Updated**: June 27, 2024  
**Status**: Production Ready  
**For Updates**: See README.md and DESIGN.md
