from sqlalchemy.orm import Session
from app.database.models import Memory, Chat, Task
from .rag_engine import rag_engine
import logging

logger = logging.getLogger(__name__)


class MemoryAgent:
    """Manages memories between PostgreSQL and ChromaDB"""
    
    @staticmethod
    def add_chat_memory(db: Session, user_id: int, message: str, response: str):
        """Save chat as memory"""
        content = f"User: {message}\nMindMate: {response}"
        
        embedding_id = rag_engine.add_memory(user_id, content, "chat")
        
        memory = Memory(
            content=content,
            category="chat",
            embedding_id=embedding_id,
            user_id=user_id
        )
        db.add(memory)
        db.commit()
        logger.info(f"✅ Chat memory saved for user {user_id}")
        return memory
    
    @staticmethod
    def add_manual_memory(db: Session, user_id: int, content: str, category: str):
        """Add manual note/achievement"""
        embedding_id = rag_engine.add_memory(user_id, content, category)
        
        memory = Memory(
            content=content,
            category=category,
            embedding_id=embedding_id,
            user_id=user_id
        )
        db.add(memory)
        db.commit()
        return memory
    
    @staticmethod
    def search_memories(user_id: int, query: str, top_k: int = 5):
        """Search memories"""
        return rag_engine.search_memories(user_id, query, top_k)
    
    @staticmethod
    def get_context_for_chat(user_id: int, message: str):
        """Get relevant context for AI chat"""
        memories = rag_engine.search_memories(user_id, message, top_k=3)
        
        if not memories:
            return ""
        
        # Only use highly relevant memories
        relevant = [m for m in memories if m['relevance'] > 0.2]
        
        if not relevant:
            return ""
        
        context = "=== PAST CONTEXT ===\n"
        for m in relevant:
            context += f"[{m['category']}] {m['content']}\n\n"
        context += "=== END CONTEXT ==="
        
        return context
    
    @staticmethod
    def sync_existing_data(db: Session, user_id: int):
        """One-time sync of old chats/tasks"""
        synced = 0
        
        # Check if already synced
        existing = db.query(Memory).filter(Memory.user_id == user_id).count()
        if existing > 0:
            return {"message": "Already synced", "existing": existing}
        
        # Sync chats
        chats = db.query(Chat).filter(Chat.user_id == user_id).all()
        for chat in chats:
            try:
                content = f"User: {chat.message}\nMindMate: {chat.response}"
                embedding_id = rag_engine.add_memory(user_id, content, "chat")
                db.add(Memory(
                    content=content,
                    category="chat",
                    embedding_id=embedding_id,
                    user_id=user_id
                ))
                synced += 1
            except Exception as e:
                logger.error(f"Sync error: {e}")
        
        # Sync tasks
        tasks = db.query(Task).filter(Task.user_id == user_id).all()
        for task in tasks:
            try:
                content = f"Task: {task.title} - {task.description} (Due: {task.due_date})"
                embedding_id = rag_engine.add_memory(user_id, content, "task")
                db.add(Memory(
                    content=content,
                    category="task",
                    embedding_id=embedding_id,
                    user_id=user_id
                ))
                synced += 1
            except Exception as e:
                logger.error(f"Sync error: {e}")
        
        db.commit()
        return {"message": "Sync complete", "synced": synced}
    
    @staticmethod
    def get_all_memories(db: Session, user_id: int, limit: int = 50):
        """Get recent memories"""
        return db.query(Memory).filter(
            Memory.user_id == user_id
        ).order_by(Memory.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def delete_memory(db: Session, memory_id: int, user_id: int):
        """Delete a memory"""
        memory = db.query(Memory).filter(
            Memory.id == memory_id,
            Memory.user_id == user_id
        ).first()
        
        if memory:
            rag_engine.delete_memory(memory.embedding_id)
            db.delete(memory)
            db.commit()
            return True
        return False


# THIS LINE IS CRITICAL - Make sure it's at the bottom
memory_agent = MemoryAgent()