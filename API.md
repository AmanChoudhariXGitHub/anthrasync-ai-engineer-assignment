# API Documentation: Enterprise Knowledge Assistant

## Base URL

```
http://localhost:8000
```

## Automatic Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Authentication

Currently no authentication required. For production, implement OAuth2:

```python
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

## Common Response Format

### Success Response

```json
{
  "status": "success",
  "data": { /* ... */ }
}
```

### Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Endpoints

---

## 1. Health Check

### GET `/health`

Check if the API and all services are operational.

**Request:**
```bash
curl -X GET http://localhost:8000/health
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "vector_store": true,
  "rag_chain": true
}
```

**Use Case**: Startup verification, load balancer health checks

---

## 2. Root Endpoint

### GET `/`

Get API information and available endpoints.

**Request:**
```bash
curl -X GET http://localhost:8000/
```

**Response (200 OK):**
```json
{
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
```

---

## 3. Upload Document

### POST `/upload`

Process and add a document to the knowledge base.

**Supported Formats**: PDF, DOCX, TXT

**Request:**
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf"
```

**Request Details:**
- **Content-Type**: `multipart/form-data`
- **Field**: `file` (binary, required)
- **Max Size**: 100MB (configurable)

**Response (200 OK):**
```json
{
  "status": "success",
  "filename": "document.pdf",
  "chunks": 42,
  "message": "Successfully processed 42 chunks"
}
```

**Error Responses:**

| Status | Condition | Example |
|--------|-----------|---------|
| 400 | Unsupported file type | `{"detail": "File type not supported"}` |
| 413 | File too large | `{"detail": "File size exceeds limit"}` |
| 500 | Processing error | `{"detail": "Error extracting text from PDF"}` |
| 503 | Service unavailable | `{"detail": "Vector store not initialized"}` |

**Examples:**

Python:
```python
import requests

with open('my_document.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/upload', files=files)
    print(response.json())
```

JavaScript:
```javascript
const formData = new FormData();
formData.append('file', document.getElementById('fileInput').files[0]);

fetch('http://localhost:8000/upload', {
  method: 'POST',
  body: formData
})
.then(r => r.json())
.then(data => console.log(data));
```

---

## 4. Query Knowledge Base

### POST `/query`

Ask a question and get an answer with source attribution.

**Request:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main findings?",
    "top_k": 5,
    "max_tokens": 512
  }'
```

**Request Body:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `question` | string | required | The question to answer |
| `top_k` | integer | 5 | Number of documents to retrieve (1-10) |
| `max_tokens` | integer | 512 | Maximum response length (100-2048) |

**Response (200 OK):**
```json
{
  "question": "What are the main findings?",
  "answer": "According to the provided documents, the main findings include...",
  "sources": [
    {
      "filename": "report.pdf",
      "relevance": 0.89,
      "chunk_id": 3
    },
    {
      "filename": "summary.docx",
      "relevance": 0.76,
      "chunk_id": 1
    }
  ],
  "retrieval_count": 2,
  "model": "mistral"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `question` | string | The input question (echo) |
| `answer` | string | The generated answer |
| `sources` | array | Retrieved documents with relevance scores |
| `retrieval_count` | integer | Number of documents used |
| `model` | string | Model used for generation |

**Error Responses:**

| Status | Condition |
|--------|-----------|
| 400 | Empty question |
| 503 | RAG chain not initialized |
| 500 | Processing error |

**Latency Expectations:**
- Queries take 10-50 seconds
- Emoji + question answering in 5-30s
- LLM generation: 5-30s
- Retrieval + formatting: <2s

**Advanced Examples:**

Python with streaming:
```python
import requests
import json

response = requests.post(
  'http://localhost:8000/query',
  json={
    'question': 'Explain the methodology',
    'top_k': 3,
    'max_tokens': 1024
  },
  stream=True
)

for line in response.iter_lines():
    print(line.decode('utf-8'))
```

JavaScript:
```javascript
const response = await fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'What is the budget?',
    top_k: 5,
    max_tokens: 512
  })
});

const data = await response.json();
console.log(`Answer: ${data.answer}`);
console.log(`Sources: ${data.sources.length} documents`);
```

---

## 5. Get Collection Info

### GET `/collection-info`

Retrieve statistics about the stored documents.

**Request:**
```bash
curl -X GET http://localhost:8000/collection-info
```

**Response (200 OK):**
```json
{
  "total_chunks": 1250,
  "embedding_model": "all-MiniLM-L6-v2",
  "status": "ready"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `total_chunks` | integer | Total document chunks stored |
| `embedding_model` | string | Embedding model in use |
| `status` | string | Collection status ("ready", "initializing", etc.) |

**Use Cases**:
- Monitor knowledge base size
- Verify documents are indexed
- Pre-flight checks before queries

---

## 6. Clear Collection

### DELETE `/collection`

Remove all documents from the vector store.

**Request:**
```bash
curl -X DELETE http://localhost:8000/collection
```

**Response (200 OK):**
```json
{
  "status": "success",
  "cleared_chunks": 1250,
  "message": "Collection cleared successfully"
}
```

**⚠️ Warning**: This operation is irreversible!

**Use Cases**:
- Reset for new project
- Clean up test data
- Restart indexing

---

## 7. Evaluate Response

### POST `/evaluate`

Evaluate a generated answer against a reference using multiple metrics.

**Request:**
```bash
curl -X POST "http://localhost:8000/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the capital of France?",
    "reference_answer": "The capital of France is Paris.",
    "generated_answer": "Paris is the capital city of France."
  }'
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | string | The question (for context) |
| `reference_answer` | string | Ground truth answer |
| `generated_answer` | string | System-generated answer |

**Response (200 OK):**
```json
{
  "question": "What is the capital of France?",
  "bleu_score": 0.892,
  "rouge_scores": {
    "rouge1_precision": 0.85,
    "rouge1_recall": 0.80,
    "rouge1_fmeasure": 0.825,
    "rougeL_precision": 0.85,
    "rougeL_recall": 0.80,
    "rougeL_fmeasure": 0.825
  },
  "token_overlap": {
    "jaccard_similarity": 0.75,
    "token_precision": 0.80,
    "token_recall": 0.70
  },
  "answer_length_generated": 12,
  "answer_length_reference": 10
}
```

**Metric Explanations:**

### BLEU Score (0-1)
- Measures n-gram overlap
- Higher is better
- Good for exact match similarity

### ROUGE Scores (0-1)
- **Precision**: How much of generated is in reference
- **Recall**: How much of reference is in generated
- **F-measure**: Harmonic mean (use this)
- Higher is better

### Token Overlap (0-1)
- **Jaccard**: |intersection| / |union| of tokens
- **Precision**: Overlap / Generated tokens
- **Recall**: Overlap / Reference tokens
- Higher is better

**Interpretation Guide:**

| Score Range | Quality | Interpretation |
|-----------|---------|-----------------|
| 0.8-1.0 | Excellent | Nearly identical answers |
| 0.6-0.8 | Good | Similar with minor differences |
| 0.4-0.6 | Fair | Some overlap, notable differences |
| 0.2-0.4 | Poor | Significant divergence |
| 0.0-0.2 | Very Poor | Minimal similarity |

**Examples:**

Python Evaluation Script:
```python
import requests

def evaluate_rag_system(question, reference, generated):
    response = requests.post(
        'http://localhost:8000/evaluate',
        json={
            'question': question,
            'reference_answer': reference,
            'generated_answer': generated
        }
    )
    
    metrics = response.json()
    print(f"BLEU: {metrics['bleu_score']:.3f}")
    print(f"ROUGE-1 F1: {metrics['rouge_scores']['rouge1_fmeasure']:.3f}")
    print(f"Jaccard: {metrics['token_overlap']['jaccard_similarity']:.3f}")
    
    return metrics

# Test
q = "What are the benefits?"
ref = "The benefits include improved efficiency and cost reduction."
gen = "Benefits include efficiency improvements and reduced costs."

evaluate_rag_system(q, ref, gen)
```

---

## Rate Limiting (Recommended for Production)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/query")
@limiter.limit("30/minute")
async def query(request: QueryRequest):
    # ...
```

---

## Error Handling

All errors follow this format:

```json
{
  "detail": "Descriptive error message"
}
```

**Common Error Codes:**

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Bad Request | Check your request parameters |
| 404 | Not Found | Check the endpoint URL |
| 409 | Conflict | Resource already exists |
| 413 | Payload Too Large | File is too large (max 100MB) |
| 500 | Internal Server Error | Server-side issue, check logs |
| 503 | Service Unavailable | Service initializing, retry later |

---

## Pagination (Future)

Future versions may support pagination for large result sets:

```json
{
  "results": [...],
  "total": 100,
  "page": 1,
  "per_page": 20
}
```

---

## Webhooks (Future)

Planned for async operations:

```python
@app.post("/upload-async")
async def upload_async(file: UploadFile, webhook_url: str):
    # Process asynchronously
    # Call webhook_url with results when complete
```

---

## Version Information

- **API Version**: 1.0.0
- **Last Updated**: June 27, 2024
- **Python**: 3.10+
- **FastAPI**: 0.104+

---

## Support & Debugging

### Enable Debug Mode

```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check API Logs

```bash
# Watch real-time logs
tail -f /var/log/rag_api.log

# Search for errors
grep ERROR /var/log/rag_api.log
```

### Common Issues

**Q: Getting 503 "Service Unavailable"**
- A: Vector store not initialized. Check if backend started correctly.

**Q: Queries timing out**
- A: Increase timeout in client. LLM inference takes 15-30s.

**Q: Getting low quality answers**
- A: Add more documents or refine chunks. Try with fewer retrieval docs.

---

## Testing the API

### Using cURL

```bash
# Test health
curl -X GET http://localhost:8000/health

# Upload document
curl -X POST http://localhost:8000/upload \
  -F "file=@test.pdf"

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is this about?"}'

# Get stats
curl -X GET http://localhost:8000/collection-info

# Evaluate
curl -X POST "http://localhost:8000/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"question":"q","reference_answer":"r","generated_answer":"g"}'

# Clear
curl -X DELETE http://localhost:8000/collection
```

### Using Python

```python
import requests

# Test all endpoints
base_url = "http://localhost:8000"

# Health check
print("Health:", requests.get(f"{base_url}/health").json())

# Upload
files = {"file": open("test.pdf", "rb")}
print("Upload:", requests.post(f"{base_url}/upload", files=files).json())

# Query
response = requests.post(
    f"{base_url}/query",
    json={"question": "What?", "top_k": 5}
)
print("Query:", response.json())

# Stats
print("Stats:", requests.get(f"{base_url}/collection-info").json())
```

---

**For detailed examples and integration guides, see the main README.md**
