from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal, get_db
from app.database import models
from app.routes.auth import get_current_user
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== DAILY HIGH-FIVE (STREAKS) ====================

@router.post("/highfive")
def mark_daily_highfive(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Mark today's high-five (updates streak)"""
    
    streak = db.query(models.Streak).filter(
        models.Streak.user_id == current_user.id,
        models.Streak.streak_type == "daily_highfive"
    ).first()
    
    today = datetime.utcnow().date()
    
    if not streak:
        # Create new streak
        streak = models.Streak(
            user_id=current_user.id,
            streak_type="daily_highfive",
            current_streak=1,
            longest_streak=1,
            last_activity_date=datetime.utcnow()
        )
        db.add(streak)
    else:
        last_date = streak.last_activity_date.date() if streak.last_activity_date else None
        
        if last_date == today:
            return {"message": "Already marked today!", "current_streak": streak.current_streak}
        
        # Check if consecutive day
        if last_date == today - timedelta(days=1):
            streak.current_streak += 1
        else:
            streak.current_streak = 1  # Reset streak
        
        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
        streak.last_activity_date = datetime.utcnow()
    
    db.commit()
    db.refresh(streak)
    
    # Check for milestone achievements
    if streak.current_streak in [7, 30, 100]:
        _create_streak_milestone(db, current_user.id, streak.current_streak)
    
    return {
        "message": "High-five marked! 🙌",
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak
    }


@router.get("/streaks")
def get_all_streaks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all streak data for the week"""
    
    streak = db.query(models.Streak).filter(
        models.Streak.user_id == current_user.id,
        models.Streak.streak_type == "daily_highfive"
    ).first()
    
    if not streak:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "week_status": _get_week_status(current_user.id, db)
        }
    
    return {
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "week_status": _get_week_status(current_user.id, db)
    }


def _get_week_status(user_id: int, db: Session) -> List[Dict]:
    """Get high-five status for current week (Mon-Sun)"""
    
    today = datetime.utcnow().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    
    week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    week_status = []
    
    streak = db.query(models.Streak).filter(
        models.Streak.user_id == user_id,
        models.Streak.streak_type == "daily_highfive"
    ).first()
    
    for i, day in enumerate(week_days):
        date = start_of_week + timedelta(days=i)
        is_completed = False
        
        if streak and streak.last_activity_date:
            # Check if this day was marked
            # For now, simplified logic - you can enhance with activity log
            is_completed = (date <= today and streak.current_streak >= (today - date).days)
        
        week_status.append({
            "day": day,
            "date": str(date),
            "completed": is_completed
        })
    
    return week_status


# ==================== MOTIVATION MEMORIES ====================


@router.get("/memories/motivational")
def get_motivational_memories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all motivational memories"""
    
    memories = db.query(models.MotivationalMemory).filter(
        models.MotivationalMemory.user_id == current_user.id
    ).order_by(models.MotivationalMemory.created_at.desc()).limit(10).all()
    
    return {
        "total": len(memories),
        "memories": [
            {
                "id": m.id,
                "content": m.content,
                "emoji": m.emoji,
                "type": m.memory_type,
                "created_at": m.created_at.isoformat()
            }
            for m in memories
        ]
    }


def _create_streak_milestone(db: Session, user_id: int, streak_count: int):
    """Auto-create milestone memory for streak achievements"""
    
    messages = {
        7: "First week streak unlocked! 🔥",
        30: "30-day streak champion! 🏆",
        100: "100-day legend! You're unstoppable! 💯"
    }
    
    if streak_count in messages:
        memory = models.MotivationalMemory(
            user_id=user_id,
            content=messages[streak_count],
            emoji="🔥" if streak_count == 7 else "🏆",
            memory_type="streak_unlock"
        )
        db.add(memory)
        db.commit()


# ==================== USER PROFILE ====================

@router.get("/me")
def get_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get user profile with stats"""
    
    # Get streak data
    streak = db.query(models.Streak).filter(
        models.Streak.user_id == current_user.id,
        models.Streak.streak_type == "daily_highfive"
    ).first()
    
    # Get task completion stats
    total_tasks = db.query(models.Task).filter(
        models.Task.user_id == current_user.id
    ).count()
    
    completed_tasks = db.query(models.Task).filter(
        models.Task.user_id == current_user.id,
        models.Task.is_completed == True
    ).count()
    
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "stats": {
            "current_streak": streak.current_streak if streak else 0,
            "longest_streak": streak.longest_streak if streak else 0,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
        }
    }


# ==================== DATA & PRIVACY ====================

@router.delete("/data/clear-all")
def clear_all_data(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete all user data (tasks, chats, memories)"""
    
    # Delete all related data
    db.query(models.Chat).filter(models.Chat.user_id == current_user.id).delete()
    db.query(models.Task).filter(models.Task.user_id == current_user.id).delete()
    db.query(models.BagItem).filter(models.BagItem.user_id == current_user.id).delete()
    db.query(models.Memory).filter(models.Memory.user_id == current_user.id).delete()
    db.query(models.Streak).filter(models.Streak.user_id == current_user.id).delete()
    db.query(models.MotivationalMemory).filter(models.MotivationalMemory.user_id == current_user.id).delete()
    
    db.commit()
    
    return {"message": "All data cleared successfully"}


@router.get("/data/export")
def export_user_data(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Export all user data as JSON"""
    
    chats = db.query(models.Chat).filter(models.Chat.user_id == current_user.id).all()
    tasks = db.query(models.Task).filter(models.Task.user_id == current_user.id).all()
    memories = db.query(models.Memory).filter(models.Memory.user_id == current_user.id).all()
    
    return {
        "user": {
            "name": current_user.name,
            "email": current_user.email
        },
        "chats": [{"message": c.message, "response": c.response} for c in chats],
        "tasks": [{"title": t.title, "due_date": t.due_date, "completed": t.is_completed} for t in tasks],
        "memories": [{"content": m.content, "category": m.category} for m in memories]
    }


# ==================== HELP & SUPPORT ====================

@router.get("/help/faq")
def get_faq():
    """Get frequently asked questions"""
    return {
        "faqs": [
            {
                "question": "How does the smart planner work?",
                "answer": "MindMate uses AI to extract tasks from your chat and automatically adds them to your planner with priorities."
            },
            {
                "question": "What are streaks?",
                "answer": "Streaks track your daily consistency. Mark a high-five every day to build your streak!"
            },
            {
                "question": "How does the bag checker work?",
                "answer": "Based on your class schedule, MindMate suggests items you need to pack."
            }
        ]
    }


@router.post("/help/feedback")
def submit_feedback(
    message: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Submit user feedback"""
    
    # In production, save to database or send email
    logger.info(f"Feedback from user {current_user.id}: {message}")
    
    return {"message": "Thank you for your feedback! 💙"}


# ==================== ABOUT ====================

@router.get("/about")
def get_about():
    """Get app information"""
    return {
        "app_name": "MindMate",
        "version": "2.0.0",
        "description": "Your AI-powered student companion with memory, planning, and productivity features",
        "features": [
            "Multi-agent AI chat",
            "Smart task extraction",
            "Procrastination detection",
            "Memory & achievement tracking",
            "Smart bag checker",
            "Streak tracking"
        ],
        "developers": "MindMate Team",
        "contact": "support@mindmate.app"
    }