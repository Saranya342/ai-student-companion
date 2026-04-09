from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.database.connection import SessionLocal
from app.database import models
from app.routes.auth import get_current_user
import requests
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


# =========================
# REQUEST MODELS
# =========================
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: str        # format: "2026-04-05"
    priority: str = "medium"  # "high", "medium", "low"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    is_completed: Optional[bool] = None


# =========================
# AI STUDY PLAN GENERATOR
# =========================
def generate_study_plan(tasks: list) -> str:
    if not tasks:
        return "No tasks found. Add some tasks first!"

    task_list = "\n".join([
        f"- {t.title} (Due: {t.due_date}, Priority: {t.priority})"
        for t in tasks if not t.is_completed
    ])

    if not task_list:
        return "All tasks are completed! Great job! 🎉"

    prompt = f"""You are MindMate, a student AI companion.
A student has these pending tasks:
{task_list}

Create a short, friendly day-by-day study plan to complete all tasks on time.
Be encouraging, use Gen-Z tone, keep it under 150 words.
Use emojis. Format as Day 1, Day 2 etc."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.7
    }

    try:
        res = requests.post(GROQ_URL, headers=headers, json=body, timeout=15)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("❌ AI Plan Error:", str(e))
        return "Could not generate plan right now. Try again!"


# =========================
# ROUTES
# =========================

# 🟢 GET all tasks
@router.get("/tasks")
def get_tasks(current_user: models.User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        tasks = db.query(models.Task).filter(
            models.Task.user_id == current_user.id
        ).order_by(models.Task.due_date.asc()).all()

        return {
            "total": len(tasks),
            "completed": sum(1 for t in tasks if t.is_completed),
            "pending": sum(1 for t in tasks if not t.is_completed),
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "due_date": t.due_date,
                    "priority": t.priority,
                    "is_completed": t.is_completed
                }
                for t in tasks
            ]
        }
    finally:
        db.close()


# 🟢 GET tasks by priority
@router.get("/tasks/priority/{level}")
def get_tasks_by_priority(
    level: str,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        tasks = db.query(models.Task).filter(
            models.Task.user_id == current_user.id,
            models.Task.priority == level.lower()
        ).order_by(models.Task.due_date.asc()).all()

        return {
            "priority": level,
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "due_date": t.due_date,
                    "is_completed": t.is_completed
                }
                for t in tasks
            ]
        }
    finally:
        db.close()


# 🟢 ADD a task
@router.post("/tasks/add")
def add_task(
    req: TaskCreate,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        new_task = models.Task(
            title=req.title,
            description=req.description,
            due_date=req.due_date,
            priority=req.priority,
            is_completed=False,
            user_id=current_user.id
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        print(f"✅ Task added: {req.title}")
        return {
            "message": "Task added ✅",
            "task": {
                "id": new_task.id,
                "title": new_task.title,
                "due_date": new_task.due_date,
                "priority": new_task.priority,
                "is_completed": new_task.is_completed
            }
        }
    finally:
        db.close()


# 🟢 COMPLETE a task
@router.put("/tasks/complete/{task_id}")
def complete_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        task = db.query(models.Task).filter(
            models.Task.id == task_id,
            models.Task.user_id == current_user.id
        ).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        task.is_completed = True
        db.commit()
        completed_today = db.query(models.Task).filter(
            models.Task.user_id == current_user.id,
            models.Task.is_completed == True,
            models.Task.completed_at >= datetime.utcnow().date()
        ).count()
        
        # Milestone: Completed 5 tasks in one day
        if completed_today == 5:
            motivational_memory = models.MotivationalMemory(
                user_id=current_user.id,
                content="Completed 5 tasks in a row! 🎉",
                emoji="🎉",
                memory_type="milestone"
            )
            db.add(motivational_memory)
            db.commit()
        
        # Milestone: All tasks for today completed
        pending_today = db.query(models.Task).filter(
            models.Task.user_id == current_user.id,
            models.Task.is_completed == False,
            models.Task.due_date == str(datetime.utcnow().date())
        ).count()
        
        if pending_today == 0:
            motivational_memory = models.MotivationalMemory(
                user_id=current_user.id,
                content="All tasks for today completed! 💪",
                emoji="💪",
                memory_type="milestone"
            )
            db.add(motivational_memory)
            db.commit()

        return {
            "message": f"'{task.title}' marked as complete 🎉",
            "task_id": task_id
        }
    finally:
        db.close()


# 🟢 UPDATE a task
@router.put("/tasks/update/{task_id}")
def update_task(
    task_id: int,
    req: TaskUpdate,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        task = db.query(models.Task).filter(
            models.Task.id == task_id,
            models.Task.user_id == current_user.id
        ).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if req.title is not None:
            task.title = req.title
        if req.description is not None:
            task.description = req.description
        if req.due_date is not None:
            task.due_date = req.due_date
        if req.priority is not None:
            task.priority = req.priority
        if req.is_completed is not None:
            task.is_completed = req.is_completed

        db.commit()

        return {"message": "Task updated ✅", "task_id": task_id}
    finally:
        db.close()


# 🟢 DELETE a task
@router.delete("/tasks/delete/{task_id}")
def delete_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        task = db.query(models.Task).filter(
            models.Task.id == task_id,
            models.Task.user_id == current_user.id
        ).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        db.delete(task)
        db.commit()

        return {"message": f"'{task.title}' deleted ✅"}
    finally:
        db.close()


# 🤖 AI GENERATE STUDY PLAN
@router.get("/tasks/ai-plan")
def get_ai_study_plan(current_user: models.User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        tasks = db.query(models.Task).filter(
            models.Task.user_id == current_user.id
        ).order_by(models.Task.due_date.asc()).all()

        print(f"🤖 Generating AI study plan for {current_user.email}")
        plan = generate_study_plan(tasks)

        return {
            "student": current_user.name,
            "ai_study_plan": plan
        }
    finally:
        db.close()