"""
Vector store module using ChromaDB for storing and retrieving embeddings.
Uses Sentence Transformers for generating embeddings.
"""

import os
import logging
from typing import List, Dict, Tuple
import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class VectorStore:
    """Manage vector embeddings and similarity search using ChromaDB."""
    
    def __init__(self, persist_dir: str = "./chroma_db", model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize vector store.
        
        Args:
            persist_dir: Directory to persist ChromaDB
            model_name: Sentence Transformer model name
        """
        self.persist_dir = persist_dir
        self.model_name = model_name
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_dir, exist_ok=True)
        
        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(model_name)
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Vector store initialized with model: {model_name}")
    
    def add_documents(self, documents: List[Dict]) -> Dict:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document dicts with 'filename', 'chunks', 'format'
        
        Returns:
            Summary of added documents
        """
        total_chunks = 0
        
        for doc in documents:
            filename = doc.get("filename", "unknown")
            chunks = doc.get("chunks", [])
            doc_format = doc.get("format", "")
            
            # Generate IDs and metadata
            ids = []
            metadatas = []
            documents_list = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{filename}_{i}"
                ids.append(chunk_id)
                documents_list.append(chunk)
                metadatas.append({
                    "filename": filename,
                    "format": doc_format,
                    "chunk_id": i,
                    "total_chunks": len(chunks)
                })
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(documents_list, show_progress_bar=False)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                metadatas=metadatas,
                documents=documents_list
            )
            
            total_chunks += len(chunks)
            logger.info(f"Added {len(chunks)} chunks from {filename}")
        
        return {
            "status": "success",
            "total_documents": len(documents),
            "total_chunks": total_chunks,
            "collection_size": self.collection.count()
        }
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of top results to return
        
        Returns:
            List of similar documents with scores
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query], show_progress_bar=False)[0]
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        search_results = []
        
        if results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                # Convert distance to similarity score (cosine distance to similarity)
                distance = results['distances'][0][i] if results['distances'] else 0
                similarity = 1 - (distance / 2)  # Normalize for cosine distance
                
                search_results.append({
                    "document": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "similarity_score": float(similarity)
                })
        
        return search_results
    
    def get_collection_info(self) -> Dict:
        """Get information about the collection."""
        return {
            "collection_name": self.collection.name,
            "total_chunks": self.collection.count(),
            "embedding_model": self.model_name,
            "persist_dir": self.persist_dir
        }
    
    def clear_collection(self) -> Dict:
        """Clear all data from the collection."""
        count = self.collection.count()
        self.client.delete_collection(name="documents")
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        return {
            "status": "success",
            "cleared_chunks": count,
            "message": "Collection cleared successfully"
        }
