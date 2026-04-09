from sqlalchemy.orm import Session
from app.database.models import Memory, Chat, Task
from .rag_engine import rag_engine
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class MemoryActionAgent:
    """
    Handles:
    - Storing memories, thoughts
    - Triggering features (bag check, planner, journal)
    - Fetching achievements
    """
    
    # ================== MEMORY FUNCTIONS ==================
    
    def add_chat_memory(self, db: Session, user_id: int, message: str, response: str):
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
        return memory
    
    def add_manual_memory(self, db: Session, user_id: int, content: str, category: str):
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
    
    def search_memories(self, user_id: int, query: str, top_k: int = 5) -> List[Dict]:
        """Search memories via RAG"""
        return rag_engine.search_memories(user_id, query, top_k)
    
    def get_achievements(self, user_id: int, limit: int = 3) -> List[Dict]:
        """Fetch past achievements for motivation"""
        memories = rag_engine.search_memories(user_id, "achievement success completed won aced nailed", top_k=limit)
        
        # Filter for achievements only
        achievements = [
            m for m in memories 
            if m.get('category') == 'achievement' or 'success' in m['content'].lower()
        ]
        
        logger.info(f"🏆 Retrieved {len(achievements)} achievements")
        return achievements
    
    # ================== ACTION TRIGGERS ==================
    
    def analyze_for_actions(self, message: str) -> Dict:
        """
        Analyze message to trigger other features:
        - Bag Checker
        - Journal
        - Planner
        """
        message_lower = message.lower()
        
        actions = {
            "should_check_bag": self._should_trigger_bag_check(message_lower),
            "should_save_to_journal": self._should_save_to_journal(message_lower),
            "is_achievement": self._is_achievement_mention(message_lower)
        }
        
        logger.info(f"⚡ Actions detected: {actions}")
        return actions
    
    def _should_trigger_bag_check(self, message: str) -> bool:
        """Check if bag suggestion is needed"""
        keywords = [
            "class", "tomorrow", "monday", "tuesday", "wednesday",
            "thursday", "friday", "lab", "lecture", "college"
        ]
        return any(kw in message for kw in keywords)
    
    def _should_save_to_journal(self, message: str) -> bool:
        """Check if message is journal-worthy"""
        keywords = [
            "dear diary", "feeling", "today was", "i think",
            "i feel", "my thoughts", "reflecting"
        ]
        return any(kw in message for kw in keywords)
    
    def _is_achievement_mention(self, message: str) -> bool:
        """Check if user mentioned an achievement"""
        keywords = [
            "aced", "nailed it", "completed", "finished", "won",
            "scored", "achieved", "passed", "success"
        ]
        message_lower = message.lower()
    
    # Check for percentage scores (90%, 95%, etc.)
        import re
        has_percentage = bool(re.search(r'\d+%', message))
    
    # Check for grade mentions (A+, A, B+)
        has_grade = bool(re.search(r'\b[A-F][+-]?\b', message))
    
    # Check for achievement keywords
        has_keywords = any(kw in message_lower for kw in keywords)
    
        return has_percentage or has_grade or has_keywords
    
    def get_context_for_chat(self, user_id: int, message: str):
        """Get relevant context for AI chat"""
        return rag_engine.search_memories(user_id, message, top_k=3)
    
    def get_all_memories(self, db: Session, user_id: int, limit: int = 50):
        """Get recent memories"""
        return db.query(Memory).filter(
            Memory.user_id == user_id
        ).order_by(Memory.created_at.desc()).limit(limit).all()
    
    def delete_memory(self, db: Session, memory_id: int, user_id: int):
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
    
    def sync_existing_data(self, db: Session, user_id: int):
        """Sync old chats/tasks"""
        synced = 0
        
        existing = db.query(Memory).filter(Memory.user_id == user_id).count()
        if existing > 0:
            return {"message": "Already synced", "existing": existing}
        
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
        
        db.commit()
        return {"message": "Sync complete", "synced": synced}


# Global instance
memory_action_agent = MemoryActionAgent()