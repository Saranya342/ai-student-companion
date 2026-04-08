from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.database.connection import SessionLocal
from app.database import models
from app.routes.auth import get_current_user
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class MemoryCreate(BaseModel):
    content: str
    category: str
    mood: Optional[str] = None
    unlock_date: Optional[str] = None


@router.post("/add")
def add_memory(
    req: MemoryCreate,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        # Try RAG embedding - but don't fail if it doesn't work
        embedding_id = None
        try:
            from app.agents.rag_engine import rag_engine
            embedding_id = rag_engine.add_memory(
                current_user.id,
                req.content,
                req.category
            )
        except Exception as e:
            logger.warning(f"RAG embedding skipped: {e}")
            embedding_id = str(uuid.uuid4())  # fallback unique id

        memory = models.Memory(
            content=req.content,
            category=req.category,
            mood=req.mood,
            unlock_date=req.unlock_date,
            embedding_id=embedding_id,
            user_id=current_user.id
        )
        db.add(memory)
        db.commit()
        db.refresh(memory)

        return {
            "message": "Memory added ✅",
            "id": memory.id,
            "category": memory.category,
            "mood": memory.mood,
            "unlock_date": memory.unlock_date
        }
    finally:
        db.close()


@router.get("/history")
def get_memories(
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        memories = db.query(models.Memory).filter(
            models.Memory.user_id == current_user.id
        ).order_by(models.Memory.created_at.desc()).all()

        return {
            "total": len(memories),
            "memories": [
                {
                    "id": m.id,
                    "content": m.content,
                    "category": m.category,
                    "mood": m.mood,
                    "unlock_date": m.unlock_date,
                    "created_at": str(m.created_at)
                }
                for m in memories
            ]
        }
    finally:
        db.close()


@router.get("/thoughts")
def get_thoughts(
    current_user: models.User = Depends(get_current_user)
):
    """Get only thoughts"""
    db = SessionLocal()
    try:
        thoughts = db.query(models.Memory).filter(
            models.Memory.user_id == current_user.id,
            models.Memory.category == "thought"
        ).order_by(models.Memory.created_at.desc()).all()

        return {
            "total": len(thoughts),
            "thoughts": [
                {
                    "id": t.id,
                    "content": t.content,
                    "mood": t.mood,
                    "created_at": str(t.created_at)
                }
                for t in thoughts
            ]
        }
    finally:
        db.close()


@router.get("/future-letters")
def get_future_letters(
    current_user: models.User = Depends(get_current_user)
):
    """Get only future letters"""
    db = SessionLocal()
    try:
        letters = db.query(models.Memory).filter(
            models.Memory.user_id == current_user.id,
            models.Memory.category == "future"
        ).order_by(models.Memory.created_at.desc()).all()

        from datetime import datetime
        today = datetime.now().date()

        return {
            "total": len(letters),
            "letters": [
                {
                    "id": l.id,
                    "content": l.content,
                    "unlock_date": l.unlock_date,
                    "is_unlocked": (
                        l.unlock_date is None or
                        str(today) >= l.unlock_date
                    ),
                    "created_at": str(l.created_at)
                }
                for l in letters
            ]
        }
    finally:
        db.close()


@router.post("/search")
def search_memories(
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        memories = rag_engine.search_memories(
            current_user.id,
            top_k=5
        )
        return {"results": memories}
    finally:
        db.close()


@router.delete("/{memory_id}")
def delete_memory(
    memory_id: int,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        memory = db.query(models.Memory).filter(
            models.Memory.id == memory_id,
            models.Memory.user_id == current_user.id
        ).first()

        if not memory:
            raise HTTPException(404, "Memory not found")

        # Try to delete from RAG too
        try:
            from app.agents.rag_engine import rag_engine
            if memory.embedding_id:
                rag_engine.delete_memory(memory.embedding_id)
        except Exception as e:
            logger.warning(f"RAG delete skipped: {e}")

        db.delete(memory)
        db.commit()
        return {"message": "Memory deleted ✅"}
    finally:
        db.close()