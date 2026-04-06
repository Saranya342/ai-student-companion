from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.database.connection import SessionLocal
from app.database import models
from app.routes.auth import get_current_user
import requests

router = APIRouter()

GROQ_API_KEY = "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"   # ← paste your key here
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are MindMate, a warm and supportive AI best friend for students.
You help with academic tasks, emotional well-being, and daily essentials.
Be friendly, caring, Gen-Z tone. Keep responses short (2-4 sentences)."""


def ask_groq(user_message: str, chat_history: list) -> str:
    print("🚀 ask_groq CALLED")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for chat in chat_history[-10:]:
        messages.append({"role": "user", "content": chat.message})
        messages.append({"role": "assistant", "content": chat.response})

    messages.append({"role": "user", "content": user_message})

    print("📡 Calling Groq API...")
    print("🔑 API KEY starts with:", GROQ_API_KEY[:8])

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
        print("📥 Groq status code:", res.status_code)
        print("📥 Groq raw response:", res.text)

        res.raise_for_status()
        reply = res.json()["choices"][0]["message"]["content"]
        print("✅ Groq reply:", reply)
        return reply

    except requests.exceptions.ConnectionError as e:
        print("❌ CONNECTION ERROR - No internet or Groq blocked:", str(e))
        return "Connection failed!"

    except requests.exceptions.Timeout:
        print("❌ TIMEOUT ERROR - Groq took too long")
        return "Timeout!"

    except requests.exceptions.HTTPError as e:
        print("❌ HTTP ERROR:", res.status_code, res.text)
        return f"HTTP Error {res.status_code}"

    except Exception as e:
        print("❌ UNKNOWN ERROR:", type(e).__name__, str(e))
        return "Unknown error!"


class MessageRequest(BaseModel):
    message: str


@router.post("/send")
def send_message(
    req: MessageRequest,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        print(f"\n💬 Message from {current_user.email}: {req.message}")

        history = db.query(models.Chat)\
            .filter(models.Chat.user_id == current_user.id)\
            .order_by(models.Chat.id.asc())\
            .all()

        bot_response = ask_groq(req.message, history)

        new_chat = models.Chat(
            message=req.message,
            response=bot_response,
            user_id=current_user.id
        )
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)

        return {
            "your_message": req.message,
            "bot_reply": bot_response,
            "chat_id": new_chat.id
        }

    finally:
        db.close()


@router.get("/history")
def get_chat_history(current_user: models.User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        chats = db.query(models.Chat)\
            .filter(models.Chat.user_id == current_user.id)\
            .order_by(models.Chat.id.asc())\
            .all()

        return [
            {
                "id": c.id,
                "message": c.message,
                "bot_reply": c.response
            }
            for c in chats
        ]
    finally:
        db.close()


@router.delete("/clear")
def clear_history(current_user: models.User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        db.query(models.Chat)\
            .filter(models.Chat.user_id == current_user.id)\
            .delete()
        db.commit()
        return {"message": "Chat history cleared ✅"}
    finally:
        db.close()