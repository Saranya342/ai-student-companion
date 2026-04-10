from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database import models
from app.routes.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()


class ThoughtParkingCreate(BaseModel):
    content: str


@router.post("/thought-parking")
def add_thought_parking(
    thought: ThoughtParkingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Manually add a thought parking item"""
    
    entry = models.JournalEntry(
        user_id=current_user.id,
        content=thought.content,
        entry_type="thought_parking"
    )
    db.add(entry)
    db.commit()
    
    return {"message": "Thought parked! 🅿️"}


@router.get("/thought-parking")
def get_thought_parking(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all thought parking items"""
    
    thoughts = db.query(models.JournalEntry).filter(
        models.JournalEntry.user_id == current_user.id,
        models.JournalEntry.entry_type == "thought_parking"
    ).order_by(models.JournalEntry.created_at.desc()).all()
    
    return {
        "total": len(thoughts),
        "thoughts": [
            {
                "id": t.id,
                "content": t.content,
                "created_at": t.created_at.isoformat()
            }
            for t in thoughts
        ]
    }


@router.delete("/thought-parking/{thought_id}")
def delete_thought(
    thought_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a thought parking item"""
    
    thought = db.query(models.JournalEntry).filter(
        models.JournalEntry.id == thought_id,
        models.JournalEntry.user_id == current_user.id
    ).first()
    
    if thought:
        db.delete(thought)
        db.commit()
        return {"message": "Thought deleted"}
    
    return {"error": "Not found"}