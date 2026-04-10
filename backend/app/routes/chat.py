from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.database.connection import SessionLocal
from app.database import models
from app.routes.auth import get_current_user
from app.agents.memory_action_agent import memory_action_agent
import requests
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are MindMate, a warm and supportive AI best friend for students.
You help with academic tasks, emotional well-being, and daily essentials.
Be friendly, caring, Gen-Z tone. Keep responses short (2-4 sentences)."""


def ask_groq(user_message: str, chat_history: list, context: str = "") -> str:
    """Call Groq API with optional RAG context"""
    system_prompt = SYSTEM_PROMPT
    if context:
        system_prompt += f"\n\n{context}\n\nUse this context to give personalized responses."

    messages = [{"role": "system", "content": system_prompt}]

    for chat in chat_history[-10:]:
        messages.append({"role": "user", "content": chat.message})
        messages.append({"role": "assistant", "content": chat.response})

    messages.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": 300,
        "temperature": 0.7
    }

    try:
        res = requests.post(GROQ_URL, headers=headers, json=body, timeout=15)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ Groq Error: {e}")
        return "Sorry, I'm having trouble connecting right now."


class MessageRequest(BaseModel):
    message: str


@router.post("/send")
def send_message(
    req: MessageRequest,
    current_user: models.User = Depends(get_current_user)
):
    """Original chat (no RAG)"""
    db = SessionLocal()
    try:
        history = db.query(models.Chat)\
            .filter(models.Chat.user_id == current_user.id)\
            .order_by(models.Chat.id.asc()).all()

        bot_response = ask_groq(req.message, history)

        new_chat = models.Chat(
            message=req.message,
            response=bot_response,
            user_id=current_user.id
        )
        db.add(new_chat)
        db.commit()

        return {
            "your_message": req.message,
            "bot_reply": bot_response,
            "rag_enabled": False
        }
    finally:
        db.close()


@router.post("/smart-send")
def smart_send_message(
    req: MessageRequest,
    current_user: models.User = Depends(get_current_user)
):
    """RAG-enhanced chat with memory"""
    db = SessionLocal()
    try:
        # Get chat history
        history = db.query(models.Chat)\
            .filter(models.Chat.user_id == current_user.id)\
            .order_by(models.Chat.id.asc()).all()

        # Get RAG context
        context = memory_agent.get_context_for_chat(current_user.id, req.message)

        # Call Groq with context
        bot_response = ask_groq(req.message, history, context)

        # Save to chats table
        new_chat = models.Chat(
            message=req.message,
            response=bot_response,
            user_id=current_user.id
        )
        db.add(new_chat)
        db.commit()

        # Save to memories
        memory_agent.add_chat_memory(db, current_user.id, req.message, bot_response)

        return {
            "your_message": req.message,
            "bot_reply": bot_response,
            "rag_enabled": True,
            "context_used": bool(context)
        }
    finally:
        db.close()


@router.get("/history")
def get_chat_history(current_user: models.User = Depends(get_current_user)):
    """Get chat history"""
    db = SessionLocal()
    try:
        chats = db.query(models.Chat)\
            .filter(models.Chat.user_id == current_user.id)\
            .order_by(models.Chat.id.asc()).all()

        return [{"id": c.id, "message": c.message, "bot_reply": c.response} for c in chats]
    finally:
        db.close()


@router.delete("/clear")
def clear_history(current_user: models.User = Depends(get_current_user)):
    """Clear chat history"""
    db = SessionLocal()
    try:
        db.query(models.Chat).filter(models.Chat.user_id == current_user.id).delete()
        db.commit()
        return {"message": "Chat history cleared ✅"}
    finally:
        db.close()