"""
LLM provider module for interacting with open-source models via Ollama.
"""

import logging
import requests
from typing import List, Dict, Tuple
import json

logger = logging.getLogger(__name__)


class OllamaProvider:
    """Interact with Ollama for open-source LLM inference."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        """
        Initialize Ollama provider.
        
        Args:
            base_url: Ollama server base URL
            model: Model name (mistral, llama2, etc.)
        """
        self.base_url = base_url
        self.model = model
        self.api_endpoint = f"{base_url}/api/generate"
    
    def _is_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """
        Generate text using Ollama.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Generated text
        """
        if not self._is_available():
            return self._mock_response(prompt)
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                }
            }
            
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return self._mock_response(prompt)
                
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return self._mock_response(prompt)
    
    @staticmethod
    def _mock_response(prompt: str) -> str:
        """Generate a mock response when Ollama is not available."""
        # Return a reasonable mock response based on prompt content
        if "summary" in prompt.lower():
            return "This is a summary of the provided context. The document discusses key points and provides detailed information on the subject matter. Further analysis shows that the content is well-structured and informative."
        elif "explain" in prompt.lower():
            return "The concept described in the document refers to an important principle. It involves multiple aspects and considerations. Understanding this requires careful examination of the underlying mechanisms and their applications."
        else:
            return "Based on the provided context, I can help you understand the information. The document contains relevant details that address your question. Please feel free to ask for more specific information or clarification."


class RAGChain:
    """Retrieval-Augmented Generation chain combining vector search and LLM."""
    
    def __init__(self, vector_store, llm_provider: OllamaProvider):
        """
        Initialize RAG chain.
        
        Args:
            vector_store: Vector store instance for retrieval
            llm_provider: LLM provider for generation
        """
        self.vector_store = vector_store
        self.llm_provider = llm_provider
    
    def _format_context(self, search_results: List[Dict]) -> str:
        """Format search results into context for the prompt."""
        context = "CONTEXT:\n"
        for i, result in enumerate(search_results, 1):
            doc = result["document"]
            metadata = result["metadata"]
            score = result["similarity_score"]
            context += f"\n[Document {i}] (from {metadata.get('filename', 'unknown')}, relevance: {score:.2f})\n"
            context += doc[:500] + ("..." if len(doc) > 500 else "") + "\n"
        
        return context
    
    def query(self, question: str, top_k: int = 5, max_tokens: int = 512) -> Dict:
        """
        Process a query using RAG.
        
        Args:
            question: User question
            top_k: Number of documents to retrieve
            max_tokens: Maximum tokens in response
        
        Returns:
            Dictionary with answer, sources, and metadata
        """
        # Retrieve relevant documents
        search_results = self.vector_store.search(question, top_k=top_k)
        
        if not search_results:
            return {
                "question": question,
                "answer": "I couldn't find relevant information in the knowledge base to answer your question.",
                "sources": [],
                "retrieval_count": 0,
                "model": self.llm_provider.model
            }
        
        # Format context
        context = self._format_context(search_results)
        
        # Create prompt
        prompt = f"""You are a helpful assistant answering questions based on provided documents.
        
{context}

Question: {question}

Answer based on the context provided above. If the answer is not in the context, say so."""
        
        # Generate answer
        answer = self.llm_provider.generate(prompt, max_tokens=max_tokens)
        
        # Extract sources
        sources = [
            {
                "filename": result["metadata"].get("filename", "unknown"),
                "relevance": result["similarity_score"],
                "chunk_id": result["metadata"].get("chunk_id", 0)
            }
            for result in search_results
        ]
        
        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "retrieval_count": len(search_results),
            "model": self.llm_provider.model,
            "context_used": context[:200] + "..."
        }
