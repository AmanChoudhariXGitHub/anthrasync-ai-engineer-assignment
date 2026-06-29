"""
Streamlit frontend for Enterprise Knowledge Assistant RAG system.
Provides user interface for document upload and Q&A.
"""

import streamlit as st
import requests
import json
from datetime import datetime
import os

# Configure page
st.set_page_config(
    page_title="Enterprise Knowledge Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .question-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .answer-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #0066cc;
    }
    .source-box {
        background-color: #f9f9f9;
        padding: 0.8rem;
        border-radius: 0.4rem;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.8;
    }
</style>
""", unsafe_allow_html=True)

# Get API endpoint from config
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "collection_info" not in st.session_state:
    st.session_state.collection_info = None
if "api_available" not in st.session_state:
    st.session_state.api_available = False


def check_api_health():
    """Check if API is available."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def get_collection_info():
    """Fetch collection information."""
    try:
        response = requests.get(f"{API_BASE_URL}/collection-info", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def upload_document(uploaded_file):
    """Upload document to the backend."""
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getbuffer(), uploaded_file.type)}
        response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": response.text}
    except Exception as e:
        return False, {"error": str(e)}


def query_knowledge_base(question, top_k=5, max_tokens=512):
    """Query the knowledge base."""
    try:
        payload = {
            "question": question,
            "top_k": top_k,
            "max_tokens": max_tokens
        }
        
        response = requests.post(f"{API_BASE_URL}/query", json=payload, timeout=60)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": response.text}
    except Exception as e:
        return False, {"error": str(e)}


def evaluate_answer(question, reference, generated):
    """Evaluate a generated answer."""
    try:
        params = {
            "question": question,
            "reference_answer": reference,
            "generated_answer": generated
        }
        
        response = requests.post(f"{API_BASE_URL}/evaluate", params=params, timeout=10)
        
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.warning(f"Could not evaluate: {e}")
    
    return None


# Header
st.title("📚 Enterprise Knowledge Assistant")
st.markdown("**RAG-powered Q&A system for enterprise documents**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Status
    api_status = check_api_health()
    st.session_state.api_available = api_status
    
    status_color = "🟢" if api_status else "🔴"
    st.markdown(f"{status_color} **API Status**: {'Connected' if api_status else 'Disconnected'}")
    
    if api_status:
        st.markdown(f"**API URL**: {API_BASE_URL}")
    
    # Collection Info
    st.divider()
    st.subheader("📊 Collection Stats")
    
    if api_status:
        collection_info = get_collection_info()
        if collection_info:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{collection_info['total_chunks']}</div>
                    <div class="metric-label">Total Chunks</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <div class="metric-value">{collection_info['embedding_model']}</div>
                    <div class="metric-label">Model</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ API not connected. Please start the backend server.")
    
    # Configuration options
    st.divider()
    st.subheader("🔧 Query Options")
    
    top_k = st.slider("Documents to retrieve", 1, 10, 5)
    max_tokens = st.slider("Max response tokens", 100, 1000, 512)
    
    st.divider()
    
    # Clear collection button
    if st.button("🗑️ Clear Collection", key="clear_btn"):
        try:
            response = requests.delete(f"{API_BASE_URL}/collection", timeout=5)
            if response.status_code == 200:
                st.success("Collection cleared successfully!")
            else:
                st.error("Failed to clear collection")
        except Exception as e:
            st.error(f"Error: {e}")


# Main content
if not st.session_state.api_available:
    st.error("""
    ⚠️ **Backend API is not available**
    
    Please ensure the FastAPI backend is running:
    ```bash
    cd rag_system/backend
    python main.py
    ```
    """)
else:
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload Documents", "❓ Ask Questions", "📈 Evaluate"])
    
    # Tab 1: Document Upload
    with tab1:
        st.header("Upload Documents")
        st.markdown("""
        Upload your documents to build the knowledge base.
        **Supported formats:** PDF, DOCX, TXT
        """)
        
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button("🚀 Upload Documents", key="upload_btn"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, file in enumerate(uploaded_files):
                    status_text.text(f"Uploading {i+1}/{len(uploaded_files)}: {file.name}")
                    
                    success, result = upload_document(file)
                    
                    if success:
                        st.success(f"✅ {result['filename']}: {result['chunks']} chunks processed")
                    else:
                        st.error(f"❌ {file.name}: {result.get('error', 'Unknown error')}")
                    
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                st.balloons()
    
    # Tab 2: Q&A
    with tab2:
        st.header("Ask Questions")
        
        # Display chat history
        if st.session_state.chat_history:
            st.subheader("💬 Chat History")
            for item in st.session_state.chat_history:
                with st.container():
                    st.markdown(f"<div class='question-box'><b>Q:</b> {item['question']}</div>", 
                              unsafe_allow_html=True)
                    st.markdown(f"<div class='answer-box'><b>A:</b> {item['answer']}</div>", 
                              unsafe_allow_html=True)
                    
                    if item['sources']:
                        st.markdown("**Sources:**")
                        for source in item['sources']:
                            st.markdown(f"""
                            <div class='source-box'>
                                📄 <b>{source['filename']}</b> (Relevance: {source['relevance']:.2f})
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.divider()
        
        # Input section
        st.subheader("📝 New Question")
        question = st.text_area(
            "Enter your question:",
            height=100,
            placeholder="Ask anything about your documents..."
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🔍 Ask", key="ask_btn"):
                if question.strip():
                    with st.spinner("Searching knowledge base..."):
                        success, result = query_knowledge_base(
                            question,
                            top_k=top_k,
                            max_tokens=max_tokens
                        )
                        
                        if success:
                            # Add to history
                            st.session_state.chat_history.append({
                                "question": question,
                                "answer": result['answer'],
                                "sources": result['sources'],
                                "timestamp": datetime.now().isoformat()
                            })
                            
                            st.success("Question answered!")
                            st.rerun()
                        else:
                            st.error(f"Error: {result.get('error', 'Unknown error')}")
                else:
                    st.warning("Please enter a question")
        
        with col2:
            if st.button("🗑️ Clear History"):
                st.session_state.chat_history = []
                st.rerun()
    
    # Tab 3: Evaluation
    with tab3:
        st.header("Evaluation Metrics")
        st.markdown("""
        Test your RAG system with known Q&A pairs.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            eval_question = st.text_area("Question:", key="eval_q")
            reference_answer = st.text_area("Reference Answer:", key="eval_ref")
        
        with col2:
            generated_answer = st.text_area("Generated Answer:", key="eval_gen")
            
            if st.button("📊 Evaluate"):
                if all([eval_question, reference_answer, generated_answer]):
                    with st.spinner("Evaluating..."):
                        metrics = evaluate_answer(eval_question, reference_answer, generated_answer)
                        
                        if metrics:
                            st.success("Evaluation complete!")
                            
                            # Display metrics
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                bleu = metrics.get('bleu_score', 0)
                                st.metric("BLEU Score", f"{bleu:.3f}")
                            
                            with col2:
                                rouge = metrics.get('rouge_scores', {})
                                f1 = rouge.get('rouge1_fmeasure', 0)
                                st.metric("ROUGE-1 F1", f"{f1:.3f}")
                            
                            with col3:
                                token_overlap = metrics.get('token_overlap', {})
                                jaccard = token_overlap.get('jaccard_similarity', 0)
                                st.metric("Jaccard Similarity", f"{jaccard:.3f}")
                            
                            # Detailed metrics
                            st.subheader("Detailed Metrics")
                            st.json(metrics)
                else:
                    st.warning("Please fill in all fields")


# Footer
st.divider()
st.markdown("""
---
**Enterprise Knowledge Assistant v1.0.0**  
Built with FastAPI • Streamlit • ChromaDB • Sentence Transformers
""")
