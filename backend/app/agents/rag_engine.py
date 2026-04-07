import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGEngine:
    """ChromaDB + SentenceTransformers RAG Engine"""
    
    def __init__(self):
        # ChromaDB storage path
        self.chroma_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "chroma_db"
        )
        os.makedirs(self.chroma_path, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=self.chroma_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Load embedding model (runs locally)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get/create collection
        self.collection = self.client.get_or_create_collection(
            name="mindmate_memories",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"✅ RAG Engine initialized. Memories: {self.collection.count()}")
    
    def add_memory(self, user_id: int, content: str, category: str):
        """Add memory to ChromaDB"""
        embedding_id = str(uuid.uuid4())
        embedding = self.embedding_model.encode(content).tolist()
        
        self.collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[{"user_id": user_id, "category": category}],
            ids=[embedding_id]
        )
        
        logger.info(f"✅ Memory added: {embedding_id[:8]}... (user: {user_id})")
        return embedding_id
    
    def search_memories(self, user_id: int, query: str, top_k: int = 5):
        """Search for relevant memories"""
        query_embedding = self.embedding_model.encode(query).tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count()),
            where={"user_id": user_id},
            include=["documents", "metadatas", "distances"]
        )
        
        memories = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                memories.append({
                    "content": results['documents'][0][i],
                    "category": results['metadatas'][0][i].get('category'),
                    "relevance": 1 - results['distances'][0][i]
                })
        
        return memories
    
    def delete_memory(self, embedding_id: str):
        """Delete a memory"""
        try:
            self.collection.delete(ids=[embedding_id])
            return True
        except:
            return False


# Global instance
rag_engine = RAGEngine()