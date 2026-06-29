# Enterprise Knowledge Assistant

A production-ready **Retrieval-Augmented Generation (RAG)** system for enterprise document analysis and question answering. Built with FastAPI, Streamlit, ChromaDB, and open-source LLMs.

## 🎯 Features

- **Document Processing**: Extract and chunk text from PDF, DOCX, and TXT files
- **Vector Embeddings**: Sentence Transformers for semantic search
- **Fast Retrieval**: ChromaDB for efficient similarity search
- **Open-Source LLMs**: Ollama integration for local model inference (Mistral, Llama)
- **REST API**: Production-grade FastAPI backend with full documentation
- **Interactive UI**: Streamlit frontend for document management and Q&A
- **Evaluation Metrics**: ROUGE, BLEU, and token overlap scoring
- **CORS Support**: Cross-origin requests enabled for integration
- **Error Handling**: Comprehensive logging and error management

## 📋 Architecture

```
┌─────────────────────────────────────────────────────┐
│         Streamlit Frontend (Port 8501)              │
│    (Document Upload, Q&A, Evaluation, Chat)         │
└────────────────────┬────────────────────────────────┘
                     │ HTTP Requests
                     ▼
┌─────────────────────────────────────────────────────┐
│      FastAPI Backend (Port 8000)                    │
│  ┌──────────────────────────────────────────────┐   │
│  │ Routes: /upload, /query, /evaluate, /health  │   │
│  └──────────────────────────────────────────────┘   │
└────────────────┬──────────────────┬─────────────────┘
                 │                  │
         ┌───────▼──────┐    ┌──────▼─────────┐
         │  ChromaDB    │    │  Ollama        │
         │  (Vectors)   │    │  (LLM)         │
         └──────────────┘    └────────────────┘
         
Document Processor → Vector Store → RAG Chain → LLM Response
                        ↓
                   Evaluation Module
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Ollama installed and running locally
- 4GB+ RAM recommended

### Installation

1. **Clone and setup**:
```bash
cd rag_system
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r ../requirements.txt
```

2. **Install Ollama** (if not already installed):
```bash
# Visit https://ollama.ai for installation instructions
# Download and install Ollama
```

3. **Pull a model**:
```bash
ollama pull mistral
# Or use: ollama pull llama2
```

### Running the System

**Option 1: Using the startup script**:
```bash
cd /vercel/share/v0-project
chmod +x run.sh
./run.sh
```

**Option 2: Manual startup**:

Terminal 1 - Start Ollama:
```bash
ollama serve
```

Terminal 2 - Start FastAPI backend:
```bash
cd rag_system/backend
source ../venv/bin/activate
python main.py
```

Terminal 3 - Start Streamlit frontend:
```bash
cd rag_system/frontend
source ../venv/bin/activate
streamlit run app.py
```

### Access the Application

- **UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📖 Usage Guide

### 1. Upload Documents

**Via Streamlit UI:**
1. Go to "📤 Upload Documents" tab
2. Select PDF, DOCX, or TXT files
3. Click "🚀 Upload Documents"

**Via API:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@your_document.pdf"
```

### 2. Ask Questions

**Via Streamlit UI:**
1. Go to "❓ Ask Questions" tab
2. Enter your question
3. Click "🔍 Ask"
4. View answer with source documents

**Via API:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main benefits?",
    "top_k": 5,
    "max_tokens": 512
  }'
```

### 3. Evaluate Responses

**Via Streamlit UI:**
1. Go to "📈 Evaluate" tab
2. Enter question, reference answer, and generated answer
3. Click "📊 Evaluate"
4. View BLEU, ROUGE, and token overlap scores

**Via API:**
```bash
curl -X POST "http://localhost:8000/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is X?",
    "reference_answer": "...",
    "generated_answer": "..."
  }'
```

## 🔧 API Endpoints

### Health Check
```
GET /health
```
Check if services are running.

### Upload Document
```
POST /upload
Content-Type: multipart/form-data
```
Upload a document for processing.

### Query
```
POST /query
Content-Type: application/json
```
Query the knowledge base.

**Request**:
```json
{
  "question": "What is the main topic?",
  "top_k": 5,
  "max_tokens": 512
}
```

**Response**:
```json
{
  "question": "What is the main topic?",
  "answer": "Based on the documents...",
  "sources": [
    {
      "filename": "document.pdf",
      "relevance": 0.87,
      "chunk_id": 0
    }
  ],
  "retrieval_count": 5,
  "model": "mistral"
}
```

### Get Collection Info
```
GET /collection-info
```
Get statistics about stored documents.

### Clear Collection
```
DELETE /collection
```
Remove all documents from the vector store.

### Evaluate
```
POST /evaluate
```
Evaluate a generated answer.

**Parameters**:
- `question`: The question asked
- `reference_answer`: Ground truth answer
- `generated_answer`: System-generated answer

## ⚙️ Configuration

Edit `.env` to customize:

```env
# FastAPI
API_HOST=0.0.0.0
API_PORT=8000

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# ChromaDB
CHROMA_DB_PATH=./chroma_db

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Frontend
API_BASE_URL=http://localhost:8000
```

## 📊 Evaluation Metrics

The system provides three evaluation approaches:

### 1. BLEU Score
- Measures n-gram overlap between reference and generated text
- Range: 0-1 (higher is better)
- Good for: Lexical similarity assessment

### 2. ROUGE Score
- ROUGE-1: Unigram overlap
- ROUGE-L: Longest common subsequence
- Range: 0-1 (higher is better)
- Good for: Summary quality evaluation

### 3. Token Overlap
- Jaccard Similarity: Set intersection over union
- Token Precision/Recall: Overlap metrics
- Range: 0-1 (higher is better)
- Good for: Content coverage assessment

## 🏗️ Project Structure

```
rag_system/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── document_processor.py   # Document extraction & chunking
│   ├── vector_store.py         # ChromaDB integration
│   ├── llm_provider.py         # Ollama integration & RAG chain
│   ├── evaluation.py           # Evaluation metrics
│   └── __init__.py
├── frontend/
│   ├── app.py                  # Streamlit application
│   └── __init__.py
├── data/                       # Sample documents
└── models/                     # Downloaded models
├── __init__.py
.env                            # Configuration
requirements.txt                # Dependencies
run.sh                          # Startup script
README.md                       # This file
DESIGN.md                       # Design documentation
API.md                          # API documentation
ARCHITECTURE.md                 # Architecture details
```

## 🔒 Security Considerations

- **CORS Enabled**: Configure origins in `main.py` for production
- **Input Validation**: All endpoints validate input with Pydantic
- **Error Handling**: Sensitive errors are masked in responses
- **Rate Limiting**: Consider adding rate limiting middleware for production
- **Authentication**: Add OAuth2/JWT for production deployments

## 🚨 Troubleshooting

### Ollama Not Connected
```
❌ Error: ollama: connect: no such file or directory
```
**Solution**: Start Ollama server: `ollama serve`

### Out of Memory
```
❌ Error: Memory error during embedding generation
```
**Solution**: 
- Use smaller model: `ollama pull mistral-7b`
- Reduce chunk size in `document_processor.py`
- Reduce batch size in `vector_store.py`

### Slow Performance
**Solution**:
- Use GPU-accelerated Ollama: See [Ollama GPU docs](https://github.com/ollama/ollama/blob/main/docs/gpu.md)
- Reduce `top_k` parameter in queries
- Use smaller embedding model: `DistilBERT` instead of `all-MiniLM-L6-v2`

### Vector Store Issues
```bash
# Reset vector store
rm -rf chroma_db/
```

## 📈 Performance Characteristics

| Component | Time | Notes |
|-----------|------|-------|
| Document Upload | 1-5s | Depends on file size |
| Embedding Generation | 2-10s | Per query, depends on chunk count |
| Retrieval | <100ms | Vector similarity search |
| LLM Generation | 5-30s | Depends on model and token count |
| Total Query Time | 10-50s | End-to-end latency |

## 🛠️ Development

### Running Tests
```bash
pytest rag_system/backend/
```

### Code Style
```bash
black rag_system/
flake8 rag_system/
```

### Building Docker Image
```bash
docker build -t enterprise-knowledge-assistant .
docker run -p 8000:8000 -p 8501:8501 enterprise-knowledge-assistant
```

## 📝 Sample Use Cases

1. **Enterprise Documentation Q&A**
   - Upload product documentation, FAQs, manuals
   - Answer customer questions automatically

2. **Contract Analysis**
   - Upload legal documents
   - Find clauses and terms quickly

3. **Technical Documentation**
   - API docs, code comments, tutorials
   - Quick reference for developers

4. **Knowledge Base Search**
   - Company policies, procedures
   - Internal knowledge management

## 🤝 Contributing

To contribute improvements:
1. Create a new branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## 📄 License

This project is provided as-is for evaluation purposes.

## 📞 Support

For issues or questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review API documentation at `/docs`
3. Check logs in the terminal output

## 🎓 Learning Resources

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Ollama Documentation](https://github.com/ollama/ollama)

---

**Enterprise Knowledge Assistant v1.0.0** | Built with FastAPI • Streamlit • ChromaDB • Sentence Transformers
