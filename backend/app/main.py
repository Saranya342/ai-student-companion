from fastapi import FastAPI
from app.database.connection import engine
from app.database import models
from app.api import users
from app.routes import chat, bag, planner, memory  # Added memory
from app.routes import chat, bag, planner, memory, notifications # Add notifications
from app.services.scheduler import start_scheduler
app = FastAPI()

models.Base.metadata.create_all(bind=engine)
app.include_router(notifications.router, prefix="/notifications", tags=["🔔 Notifications"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(bag.router, prefix="/bag", tags=["Bag Checker"])
app.include_router(planner.router, prefix="/planner", tags=["Planner"])
app.include_router(memory.router, prefix="/memory", tags=["Memory & RAG"])  # NEW

@app.get("/")
def home():
    return {
        "message": "MindMate AI Backend with RAG Running ✅",
        "features": ["Chat", "Smart Chat (RAG)", "Memory", "Planner", "Bag"]
    }
@app.on_event("startup")
def on_startup():
    start_scheduler()