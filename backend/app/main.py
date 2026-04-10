from fastapi import FastAPI
from app.database.connection import engine
from app.database import models
from app.api import users
from app.routes import chat, bag, planner, memory, notifications
from app.services.scheduler import start_scheduler
from app.routes import chat, bag, planner, memory, agent_chat, profile, journal
from app.routes import chat, bag, planner, memory, agent_chat, profile 

app = FastAPI(
    title="MindMate AI Backend",
    description="Gen-Z AI Student Companion with RAG",
    version="2.0"
)

# Create all database tables
models.Base.metadata.create_all(bind=engine)

# Include all routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(bag.router, prefix="/bag", tags=["Bag Checker"])
app.include_router(planner.router, prefix="/planner", tags=["Planner"])
app.include_router(memory.router, prefix="/memory", tags=["Memory & RAG"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
app.include_router(profile.router, prefix="/profile", tags=["👤 Profile"])
from app.routes import chat, bag, planner, memory, agent_chat
app.include_router(agent_chat.router, prefix="/chat", tags=["💬 Multi-Agent Chat"])
app.include_router(journal.router, prefix="/journal", tags=["📝 Journal"])
@app.get("/")
def home():
    return {
        "message": "MindMate AI Backend with RAG Running!",
        "version": "2.0",
        "features": [
            "Chat",
            "Smart Chat with RAG",
            "Memory System",
            "Planner",
            "Bag Checker",
            "Notifications"
        ]
    }

@app.on_event("startup")
def on_startup():
    start_scheduler()
    print("MindMate Backend Started!")