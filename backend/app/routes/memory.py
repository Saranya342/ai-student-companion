from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.database.connection import SessionLocal
from app.routes.auth import get_current_user
from app.agents.memory_agent import memory_agent

router = APIRouter()


class MemoryCreate(BaseModel):
    content: str
    category: str  # "note", "achievement", "reminder"


class MemorySearch(BaseModel):
    query: str
    top_k: int = 5


@router.post("/add")
def add_memory(req: MemoryCreate, current_user=Depends(get_current_user)):
    """Add a manual memory"""
    db = SessionLocal()
    try:
        memory = memory_agent.add_manual_memory(
            db, current_user.id, req.content, req.category
        )
        return {
            "message": "Memory added ✅",
            "id": memory.id,
            "category": memory.category
        }
    finally:
        db.close()


@router.post("/search")
def search_memories(req: MemorySearch, current_user=Depends(get_current_user)):
    """Search memories using RAG"""
    memories = memory_agent.search_memories(
        current_user.id, req.query, req.top_k
    )
    return {"query": req.query, "results": memories}


@router.get("/history")
def get_history(current_user=Depends(get_current_user)):
    """Get all memories"""
    db = SessionLocal()
    try:
        memories = memory_agent.get_all_memories(db, current_user.id)
        return {
            "total": len(memories),
            "memories": [
                {
                    "id": m.id,
                    "content": m.content,
                    "category": m.category,
                    "created_at": str(m.created_at)
                }
                for m in memories
            ]
        }
    finally:
        db.close()


@router.delete("/{memory_id}")
def delete_memory(memory_id: int, current_user=Depends(get_current_user)):
    """Delete a memory"""
    db = SessionLocal()
    try:
        success = memory_agent.delete_memory(db, memory_id, current_user.id)
        if success:
            return {"message": "Memory deleted ✅"}
        raise HTTPException(404, "Memory not found")
    finally:
        db.close()


@router.post("/sync")
def sync_data(current_user=Depends(get_current_user)):
    """One-time sync of existing chats/tasks"""
    db = SessionLocal()
    try:
        result = memory_agent.sync_existing_data(db, current_user.id)
        return result
    finally:
        db.close()