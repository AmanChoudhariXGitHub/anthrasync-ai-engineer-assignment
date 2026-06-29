# Quick Start Guide

Get the Enterprise Knowledge Assistant running in 5 minutes.

## Prerequisites

- Python 3.10+ (`python3 --version`)
- Ollama installed and running (`ollama serve`)
- Mistral model downloaded (`ollama pull mistral`)

## 1. Setup (2 minutes)

```bash
# Clone and navigate
cd /path/to/rag_system

# Create and activate virtual environment
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1  # or: venv\Scripts\activate (Windows)

# Install dependencies
pip install -r ../requirements.txt
```

## 2. Configure (1 minute)

Edit `.env` (optional, defaults work):
```env
OLLAMA_MODEL=mistral        # LLM to use
API_PORT=8000              # API port
CHROMA_DB_PATH=./chroma_db # Vector store location
```

## 3. Start Services (1 minute)

**Terminal 1 - Ollama**:
```bash
ollama serve
# Should see: "Ollama is listening on 127.0.0.1:11434"
```

**Terminal 2 - Backend**:
```bash
cd rag_system/backend
python main.py
# Should see: "Uvicorn running on http://0.0.0.0:8000"
```

**Terminal 3 - Frontend**:
```bash
cd rag_system/frontend
streamlit run app.py
# Should see: "You can now view your Streamlit app at http://localhost:8501"
```

## 4. Use It (1 minute)

1. **Open UI**: http://localhost:8501
2. **Upload**: Go to "📤 Upload Documents" → Select PDF/DOCX/TXT → Click "🚀 Upload"
3. **Ask**: Go to "❓ Ask Questions" → Type question → Click "🔍 Ask"
4. **Evaluate**: Go to "📈 Evaluate" → Enter answers → Click "📊 Evaluate"

## Via API

```bash
# Upload
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf"

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is this?","top_k":3}'

# API Docs
# Open: http://localhost:8000/docs
```

## 🎯 Example Workflow

```bash
# 1. Start with sample data (already in rag_system/data/)
# 2. Upload via UI or API
# 3. Ask questions
# 4. See answers with sources
```

## ⚡ Common Commands

| Task | Command |
|------|---------|
| Check health | `curl http://localhost:8000/health` |
| View API docs | Open http://localhost:8000/docs |
| View UI | Open http://localhost:8501 |
| Upload file | `curl -X POST http://localhost:8000/upload -F "file=@doc.pdf"` |
| Query | `curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"question":"What?","top_k":5}'` |
| Clear data | `curl -X DELETE http://localhost:8000/collection` |
| Stop services | Press `Ctrl+C` in each terminal |

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Ollama: connect refused" | Run `ollama serve` in a terminal |
| "Port 8000 in use" | Change API_PORT in .env or kill process: `lsof -i :8000 \| kill -9 <PID>` |
| "Slow responses (>60s)" | Check if Ollama is running. Use GPU for faster inference. |
| "ModuleNotFoundError" | Activate venv: `source venv/bin/activate` |
| "Vector store error" | Reset: `rm -rf chroma_db/` then restart |

## 📚 For More Information

- **Full Setup**: See [SETUP.md](SETUP.md)
- **API Details**: See [API.md](API.md)
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Design**: See [DESIGN.md](DESIGN.md)
- **Main Docs**: See [README.md](README.md)

## 🚀 One-Command Start (Linux/macOS)

```bash
# All in one - requires 3 terminals or background processes
./run.sh
```

## 💡 Next Steps

1. Upload your own documents
2. Test with different questions
3. Evaluate answer quality
4. Configure for your use case
5. Deploy to production (see DESIGN.md)

---

**Ready to go!** Open http://localhost:8501 and start asking questions.
