from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.database.connection import SessionLocal
from app.database import models
from app.routes.auth import get_current_user

router = APIRouter()

class MemoryCreate(BaseModel):
    content: str
    category: str = "win"

class ThoughtCreate(BaseModel):
    content: str

class FutureLetterCreate(BaseModel):
    content: str
    open_in: str

@router.post("/add")
def add_memory(req: MemoryCreate,
               current_user: models.User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        memory = models.Memory(
            content=req.content,
            category=req.category,
            user_id=current_user.id
        )
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return {"message": "Memory added ✅", "id": memory.id}
    finally:
        db.close()

@router.get("/all")
def get_memories(current_user: models.User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        memories = db.query(models.Memory).filter(
            models.Memory.user_id == current_user.id
        ).order_by(models.Memory.created_at.desc()).all()
        return [
            {
                "id": m.id,
                "content": m.content,
                "category": m.category,
                "created_at": str(m.created_at)
            }
            for m in memories
        ]
    finally:
        db.close()

@router.delete("/delete/{memory_id}")
def delete_memory(memory_id: int,
                  current_user: models.User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        memory = db.query(models.Memory).filter(
            models.Memory.id == memory_id,
            models.Memory.user_id == current_user.id
        ).first()
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        db.delete(memory)
        db.commit()
        return {"message": "Memory deleted ✅"}
    finally:
        db.close()