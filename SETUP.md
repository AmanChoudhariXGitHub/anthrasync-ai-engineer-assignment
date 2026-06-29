# Setup Guide: Enterprise Knowledge Assistant

Complete step-by-step setup instructions for the RAG system.

## 📋 Prerequisites

- **Operating System**: Linux, macOS, or Windows (with WSL2)
- **Python**: 3.10 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 5GB for models and vector stores
- **Internet**: For downloading models and dependencies

### Verify Python Installation

```bash
python3 --version
# Output should be Python 3.10.0 or higher

pip3 --version
# Output should be pip X.X.X from ...
```

---

## 🔧 Step 1: Install Ollama

The system uses Ollama to run open-source LLMs locally.

### macOS

```bash
# Download and install from https://ollama.ai
# Or use Homebrew
brew install ollama

# Verify installation
ollama --version
```

### Linux (Ubuntu/Debian)

```bash
# Download installer
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
sudo systemctl start ollama
sudo systemctl enable ollama

# Verify
ollama list
```

### Windows

```powershell
# Download installer from https://ollama.ai/download/windows
# Run the installer
# Verify in PowerShell
ollama --version
```

### Pull a Model

```bash
# Download Mistral (7B, ~5GB)
ollama pull mistral

# Alternative options:
# ollama pull llama2        # Llama 2 (7B)
# ollama pull neural-chat   # Neural Chat (7B)
# ollama pull orca-mini     # Orca Mini (3B, fastest)

# List downloaded models
ollama list

# Verify model works
ollama run mistral "Hello, who are you?"
```

**Download Times**:
- First pull: 5-10 minutes (depends on internet)
- Subsequent runs: Instant

---

## 🐍 Step 2: Clone and Setup Python Environment

### Get the Code

```bash
# Clone repository (if using git)
git clone <repository-url>
cd rag_system

# Or navigate to existing directory
cd /path/to/rag_system
```

### Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows PowerShell)
# venv\Scripts\Activate.ps1

# Activate (Windows CMD)
# venv\Scripts\activate.bat

# Verify activation (prompt should change)
which python  # Should show venv path
```

### Install Dependencies

```bash
# Ensure pip is updated
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt

# Verify installation
pip list | grep -E "fastapi|streamlit|chromadb|sentence-transformers"
```

**Installation Time**: 5-10 minutes

---

## 🚀 Step 3: Initialize the System

### Create Necessary Directories

```bash
mkdir -p rag_system/data
mkdir -p chroma_db
mkdir -p logs
```

### Test Ollama Connection

```bash
# Test if Ollama is running and accessible
curl http://localhost:11434/api/tags

# Should return something like:
# {"models":[{"name":"mistral:latest","size":4109...}]}
```

**If connection fails**:
```bash
# Make sure Ollama is running
ollama serve

# In another terminal, verify
ollama list
```

---

## 📚 Step 4: Add Sample Documents

### Create Sample Data

```bash
# Create data directory
mkdir -p rag_system/data

# Create sample documents
cat > rag_system/data/sample1.txt << 'EOF'
Enterprise Knowledge Management System

This document outlines best practices for enterprise knowledge management.

Key Principles:
1. Document all critical processes
2. Maintain version control
3. Archive historical documents
4. Ensure searchability
5. Control access to sensitive data

Implementation:
- Use centralized repository
- Establish naming conventions
- Train employees on system
- Regular backups and updates

Benefits:
- Improved efficiency
- Reduced training time
- Better decision making
- Compliance support
EOF

cat > rag_system/data/sample2.txt << 'EOF'
Q&A System Architecture

A Retrieval-Augmented Generation (RAG) system combines:

1. Document Processing
   - Text extraction
   - Chunking and tokenization
   - Metadata preservation

2. Vector Embeddings
   - Semantic representation
   - Similarity search
   - Dimension reduction

3. Language Model
   - Question understanding
   - Context synthesis
   - Answer generation

4. Evaluation
   - BLEU scoring
   - ROUGE metrics
   - User feedback

Performance Metrics:
- Latency: 10-50 seconds per query
- Accuracy: 85%+ for common questions
- Scalability: 10k+ documents supported
EOF
```

### Alternative: Use Your Own Documents

```bash
# Copy your documents to rag_system/data/
cp /path/to/your/documents/* rag_system/data/

# Verify files
ls -lh rag_system/data/
```

**Supported formats**: `.pdf`, `.docx`, `.txt`

---

## ▶️ Step 5: Start the System

### Option A: Using Startup Script

```bash
# Make script executable
chmod +x run.sh

# Run startup script
./run.sh

# Automatically starts:
# - FastAPI backend (port 8000)
# - Streamlit frontend (port 8501)
```

### Option B: Manual Startup

**Terminal 1 - Ollama**:
```bash
ollama serve
# Ollama server running on localhost:11434
```

**Terminal 2 - FastAPI Backend**:
```bash
cd rag_system/backend
source ../../venv/bin/activate
python main.py

# Output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 3 - Streamlit Frontend**:
```bash
cd rag_system/frontend
source ../../venv/bin/activate
streamlit run app.py

# Output:
# You can now view your Streamlit app in your browser.
# URL: http://localhost:8501
```

### Option C: Using Docker

```bash
# Build image
docker build -t rag-system .

# Run container
docker run -p 8000:8000 -p 8501:8501 \
  -v $(pwd)/chroma_db:/app/chroma_db \
  rag-system
```

---

## ✅ Step 6: Verify Installation

### Check Health

```bash
# API health check
curl http://localhost:8000/health

# Should return:
# {"status":"ok","vector_store":true,"rag_chain":true}
```

### Access UI

Open browser to:
- **Streamlit UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc

### Upload Sample Document

**Via UI**:
1. Go to "📤 Upload Documents" tab
2. Select a sample document from `rag_system/data/`
3. Click "🚀 Upload Documents"
4. Verify success message

**Via API**:
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@rag_system/data/sample1.txt"

# Response:
# {"status":"success","filename":"sample1.txt","chunks":8}
```

### Test Query

**Via UI**:
1. Go to "❓ Ask Questions" tab
2. Enter: "What is knowledge management?"
3. Click "🔍 Ask"
4. Verify answer and sources

**Via API**:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is knowledge management?",
    "top_k": 3,
    "max_tokens": 256
  }'
```

---

## 🔧 Configuration

### Environment Variables

Edit `.env` to customize:

```env
# API Configuration
API_HOST=0.0.0.0          # Listen on all interfaces
API_PORT=8000             # API port
API_BASE_URL=http://localhost:8000  # Frontend -> Backend

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral      # or: llama2, neural-chat

# Vector Store
CHROMA_DB_PATH=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2  # or: all-mpnet-base-v2

# Logging
LOG_LEVEL=INFO            # DEBUG, INFO, WARNING, ERROR
```

### Model Selection

**For Best Quality** (slower):
```env
EMBEDDING_MODEL=all-mpnet-base-v2
OLLAMA_MODEL=mistral
```

**For Best Speed** (lower quality):
```env
EMBEDDING_MODEL=sentence-transformers/distiluse-base-multilingual-cased-v2
OLLAMA_MODEL=orca-mini
```

**For Balanced Performance**:
```env
EMBEDDING_MODEL=all-MiniLM-L6-v2
OLLAMA_MODEL=mistral
```

---

## 📊 First Query Example

### Complete Workflow

```bash
# 1. Check system health
curl http://localhost:8000/health

# 2. Upload a document
curl -X POST http://localhost:8000/upload \
  -F "file=@rag_system/data/sample1.txt"

# 3. Check collection stats
curl http://localhost:8000/collection-info

# 4. Ask a question
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key principles of knowledge management?",
    "top_k": 3,
    "max_tokens": 512
  }'

# 5. Evaluate an answer (optional)
curl -X POST "http://localhost:8000/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key principles?",
    "reference_answer": "The key principles are: document processes, maintain version control, archive documents, ensure searchability, and control access.",
    "generated_answer": "According to the documentation, key principles include documenting critical processes, maintaining version control, archiving historical documents, ensuring searchability, and controlling access to sensitive data."
  }'
```

---

## 🐛 Troubleshooting

### Issue: "Ollama: connect: no such file or directory"

**Solution**: Start Ollama
```bash
ollama serve
```

### Issue: "Port 8000 already in use"

**Solution**: Use different port
```bash
# In .env
API_PORT=8001

# Or kill the process using port 8000
lsof -i :8000
kill -9 <PID>
```

### Issue: "Out of memory" during embedding

**Solution**: 
- Reduce chunk size in `document_processor.py`
- Use smaller embedding model
- Reduce batch size in `vector_store.py`

### Issue: "Slow response times" (>60s)

**Solution**:
- Enable GPU acceleration for Ollama
- Use a smaller model (orca-mini)
- Reduce `max_tokens` in queries

### Issue: "Vector store corruption"

**Solution**:
```bash
# Reset vector store
rm -rf chroma_db/

# Restart system
python main.py
```

### Issue: "Import error for chromadb"

**Solution**:
```bash
# Reinstall dependencies
pip install --upgrade --force-reinstall chromadb sentence-transformers
```

---

## 🔐 Security Setup

### For Local Development

Current setup is fine. `.env` is in `.gitignore`.

### For Production

```bash
# 1. Create strong API key
openssl rand -hex 32

# 2. Add to .env
API_KEY=<generated_key>

# 3. Add authentication to FastAPI
from fastapi.security import HTTPBearer
security = HTTPBearer()

# 4. Verify in requests
@app.post("/query")
async def query(request: QueryRequest, credentials = Depends(security)):
    # Verify credentials
    pass
```

### Enable HTTPS

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365

# Run with SSL
uvicorn main:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

---

## 📈 Performance Tuning

### Recommended for Production

1. **Use GPU for Ollama**:
```bash
# Check GPU support
ollama -h | grep gpu

# Run with GPU
CUDA_VISIBLE_DEVICES=0 ollama serve
```

2. **Use Connection Pool**:
```python
# In vector_store.py
from chromadb.config import Settings
settings = Settings(
    chroma_db_impl="duckdb+parquet",
    is_persistent=True,
    anonymized_telemetry=False
)
```

3. **Add Caching**:
```python
from functools import lru_cache
@lru_cache(maxsize=128)
def get_embeddings(text):
    # Cache embeddings for repeated queries
    pass
```

4. **Use Async I/O**:
```python
# Already implemented in FastAPI
@app.post("/query")
async def query(request: QueryRequest):
    # Async processing
    pass
```

---

## 📚 Next Steps

1. **Upload Your Data**: Add enterprise documents to test
2. **Configure Model**: Choose embedding and LLM models
3. **Fine-tune Prompts**: Adjust system prompts in `llm_provider.py`
4. **Add Authentication**: Implement for production
5. **Set Up Monitoring**: Log queries and evaluate quality
6. **Deploy**: Use Docker/Kubernetes for production

---

## 📞 Support Resources

- **Ollama Docs**: https://github.com/ollama/ollama
- **ChromaDB Docs**: https://docs.trychroma.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Streamlit Docs**: https://docs.streamlit.io/
- **Issues**: Check project repository

---

**Setup Time**: ~30 minutes
**First Query Time**: ~20 seconds
**Memory Usage**: ~2-4GB

For detailed API documentation, see [API.md](API.md)
For architecture details, see [DESIGN.md](DESIGN.md)
