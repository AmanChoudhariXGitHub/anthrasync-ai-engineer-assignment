"""
LLM provider module for interacting with Groq's LLM API.
Supports free tier with model fallback options.
"""

import logging
import os
from typing import List, Dict, Optional
from groq import Groq

logger = logging.getLogger(__name__)


class GroqProvider:
    """Interact with Groq API for LLM inference using free tier."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize Groq provider.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: Primary model name
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY not set. Using mock responses.")
            self.api_key = None
        
        self.model = model
        self.fallback_models = os.getenv("GROQ_FALLBACK_MODELS", 
                                         "llama-3.1-70b-versatile,llama-3.1-8b-instant,gemma2-9b-it").split(",")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.current_model = model
    
    def _try_model(self, client: Groq, prompt: str, model: str, max_tokens: int, 
                   temperature: float) -> Optional[str]:
        """Try to generate with a specific model."""
        try:
            message = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text.strip()
        except Exception as e:
            logger.warning(f"Failed with model {model}: {e}")
            return None
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """
        Generate text using Groq API with fallback models.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Generated text
        """
        if not self.client:
            return self._mock_response(prompt)
        
        # Try primary model first
        try:
            result = self._try_model(self.client, prompt, self.model, max_tokens, temperature)
            if result:
                self.current_model = self.model
                return result
        except Exception as e:
            logger.warning(f"Primary model {self.model} failed: {e}")
        
        # Try fallback models
        for fallback_model in self.fallback_models:
            fallback_model = fallback_model.strip()
            try:
                logger.info(f"Trying fallback model: {fallback_model}")
                result = self._try_model(self.client, prompt, fallback_model, max_tokens, temperature)
                if result:
                    self.current_model = fallback_model
                    logger.info(f"Successfully used fallback model: {fallback_model}")
                    return result
            except Exception as e:
                logger.warning(f"Fallback model {fallback_model} failed: {e}")
                continue
        
        # Fall back to mock response
        logger.error("All models failed, using mock response")
        return self._mock_response(prompt)
    
    @staticmethod
    def _mock_response(prompt: str) -> str:
        """Generate a mock response when API is not available."""
        if "summary" in prompt.lower():
            return "This is a summary of the provided context. The document discusses key points and provides detailed information on the subject matter. Further analysis shows that the content is well-structured and informative."
        elif "explain" in prompt.lower():
            return "The concept described in the document refers to an important principle. It involves multiple aspects and considerations. Understanding this requires careful examination of the underlying mechanisms and their applications."
        else:
            return "Based on the provided context, I can help you understand the information. The document contains relevant details that address your question. Please feel free to ask for more specific information or clarification."


class RAGChain:
    """Retrieval-Augmented Generation chain combining vector search and LLM."""
    
    def __init__(self, vector_store, llm_provider: GroqProvider):
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
