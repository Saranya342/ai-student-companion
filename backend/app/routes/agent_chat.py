from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.database.connection import SessionLocal
from app.database import models
from app.routes.auth import get_current_user
from app.agents.orchestrator import orchestrator
from app.agents.memory_action_agent import memory_action_agent
from app.agents.task_intelligence_agent import task_intelligence_agent
import requests
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class ChatRequest(BaseModel):
    message: str


def build_agent_prompt(message: str, agent_results: dict, bag_suggestions: list = None) -> str:
    """Build enhanced prompt using all agent insights"""
    
    emotion = agent_results['emotion_data']
    
    # Base system prompt
    system_prompt = f"""You are MindMate, a Gen-Z AI best friend for students.

**User's Emotion:** {emotion['emotion']}
**User's Vibe:** {emotion['vibe']}
**Response Tone:** {emotion['response_tone']}

**Important Guidelines:**
"""
    
    # Add vibe matching
    if emotion['should_match_casual']:
        system_prompt += f"- User used casual words: {', '.join(emotion['vibe_words'])}. Match their casual tone!\n"
    
    # Add achievements if user is down
    if agent_results['achievements']:
        achievements_text = "\n".join([f"  • {a['content']}" for a in agent_results['achievements']])
        system_prompt += f"\n**Remind them of past achievements:**\n{achievements_text}\n"
    
    # Add tasks if extracted
    if agent_results['tasks']:
        tasks_text = "\n".join([f"  • {t['title']} (Due: {t['due_date']}, Priority: {t['priority']})" for t in agent_results['tasks']])
        system_prompt += f"\n**Tasks mentioned:**\n{tasks_text}\n"
    
    # Add micro-tasks if generated
    if agent_results['micro_tasks']:
        micro_text = "\n".join([
            f"  {m['step']}. {m['task']}" 
            for m in agent_results['micro_tasks']['micro_tasks']
        ])
        system_prompt += f"\n**Break it down into steps:**\n{micro_text}\n"
    
    # Add procrastination nudge
    if agent_results.get('procrastination_data', {}).get('is_procrastinating'):
        system_prompt += f"\n**User is procrastinating:** {agent_results.get('motivational_nudge', '')}\n"
    
    # Add thought parking acknowledgment
    if agent_results['actions']['should_save_to_journal']:
        system_prompt += "\n**User shared a random thought/reminder - acknowledge it casually**\n"
    
    # Add bag check suggestions
    if bag_suggestions and len(bag_suggestions) > 0:
        day = bag_suggestions[0]['day']
        items_text = ", ".join(bag_suggestions[0]['items'])
        system_prompt += f"\n**Bag reminder for {day}:** Don't forget to pack: {items_text}\n"
        system_prompt += "- Mention the bag items casually in your response\n"
    
    system_prompt += f"\n**User Message:** {message}\n\n"
    system_prompt += "Respond naturally, empathetically, and incorporate the insights above smoothly. Keep it short (2-3 sentences unless explaining)."
    
    return system_prompt


def generate_response(message: str, agent_results: dict, bag_suggestions: list = None) -> str:
    """Generate AI response using Groq"""
    
    system_prompt = build_agent_prompt(message, agent_results, bag_suggestions)
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    body = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        "max_tokens": 400,
        "temperature": 0.7
    }
    
    try:
        res = requests.post(GROQ_URL, headers=headers, json=body, timeout=15)
        res.raise_for_status()
        response = res.json()["choices"][0]["message"]["content"]
        logger.info(f"✅ Generated response: {response[:50]}...")
        return response
        
    except Exception as e:
        logger.error(f"❌ Groq API error: {e}")
        return "Sorry, I'm having trouble connecting right now. Can you try again?"


@router.post("/agent")
def agent_chat(
    req: ChatRequest,
    current_user: models.User = Depends(get_current_user)
):
    """
    🤖 Multi-Agent Chat Endpoint
    
    Uses all 5 agents:
    1. Orchestrator routes the message
    2. Emotion + Vibe detects mood
    3. Task Intelligence extracts tasks
    4. Productivity breaks down tasks
    5. Memory & Action triggers features
    """
    
    db = SessionLocal()
    
    try:
        logger.info(f"💬 Agent chat from user {current_user.id}: {req.message[:50]}...")
        
        # Step 1: Route to agents
        agent_results = orchestrator.route(current_user.id, req.message, db)
        
        # Step 1.5: Auto-suggest bag items if needed
        bag_suggestions = []
        if agent_results['actions']['should_check_bag']:
            message_lower = req.message.lower()
            days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            detected_day = None
            
            # Detect day from message
            for day in days:
                if day in message_lower:
                    detected_day = day.capitalize()
                    break
            
            # If "tomorrow" is mentioned
            if not detected_day and "tomorrow" in message_lower:
                tomorrow_idx = (datetime.now().weekday() + 1) % 7
                detected_day = days[tomorrow_idx].capitalize()
            
            # If "today" is mentioned
            if not detected_day and "today" in message_lower:
                today_idx = datetime.now().weekday()
                detected_day = days[today_idx].capitalize()
            
            if detected_day:
                # Get or create bag items for that day
                items = db.query(models.BagItem).filter(
                    models.BagItem.user_id == current_user.id,
                    models.BagItem.day == detected_day
                ).all()
                
                # Create defaults if none exist
                if not items:
                    from app.routes.bag import DEFAULT_ITEMS
                    if detected_day in DEFAULT_ITEMS:
                        for item_name in DEFAULT_ITEMS[detected_day]:
                            new_item = models.BagItem(
                                day=detected_day,
                                item_name=item_name,
                                is_checked="false",
                                user_id=current_user.id
                            )
                            db.add(new_item)
                        db.commit()
                        
                        # Reload items
                        items = db.query(models.BagItem).filter(
                            models.BagItem.user_id == current_user.id,
                            models.BagItem.day == detected_day
                        ).all()
                
                if items:
                    bag_suggestions = [{
                        "day": detected_day,
                        "items": [i.item_name for i in items]
                    }]
                    logger.info(f"🎒 Suggested {len(items)} bag items for {detected_day}")
        
        # Step 2: Generate AI response (with bag suggestions)
        response = generate_response(req.message, agent_results, bag_suggestions)
        
        # Step 3: Save chat to database
        new_chat = models.Chat(
            message=req.message,
            response=response,
            user_id=current_user.id
        )
        db.add(new_chat)
        db.commit()
        
        # Step 4: Save to memory (RAG)
        memory_action_agent.add_chat_memory(db, current_user.id, req.message, response)
        
        # Step 5: Auto-add tasks to planner (if extracted)
        tasks_added = 0
        if agent_results['tasks']:
            tasks_added = task_intelligence_agent.add_to_planner(db, current_user.id, agent_results['tasks'])
            logger.info(f"📋 Auto-added {tasks_added} tasks to planner")
        
        # Step 6: Auto-save achievement to motivational memories
        if agent_results['actions']['is_achievement']:
            achievement_content = req.message
            
            motivational_memory = models.MotivationalMemory(
                user_id=current_user.id,
                content=achievement_content,
                emoji="🎉",
                memory_type="achievement"
            )
            db.add(motivational_memory)
            db.commit()
            
            logger.info(f"✨ Auto-saved achievement to motivational memories")
        
        # Step 7: Auto-save thought parking to journal
        if agent_results['actions']['should_save_to_journal']:
            journal_entry = models.JournalEntry(
                user_id=current_user.id,
                content=req.message,
                entry_type="thought_parking"
            )
            db.add(journal_entry)
            db.commit()
            
            logger.info(f"📝 Auto-saved thought parking to journal")
        
        logger.info(f"✅ Agent chat complete. {len(agent_results['agents_used'])} agents used")
        
        return {
            "response": response,
            "emotion_detected": agent_results['emotion_data']['emotion'],
            "vibe_detected": agent_results['emotion_data']['vibe'],
            "agents_used": agent_results['agents_used'],
            "tasks_extracted": len(agent_results['tasks']),
            "tasks_added_to_planner": tasks_added,
            "micro_tasks_generated": len(agent_results['micro_tasks']['micro_tasks']) if agent_results['micro_tasks'] else 0,
            "bag_suggestions": bag_suggestions,
            "actions_triggered": {
                "bag_check": agent_results['actions']['should_check_bag'],
                "journal_saved": agent_results['actions']['should_save_to_journal'],
                "achievement_saved": agent_results['actions']['is_achievement']
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Agent chat error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        db.close()


@router.get("/agent/history")
def get_agent_chat_history(
    current_user: models.User = Depends(get_current_user)
):
    """Get chat history"""
    db = SessionLocal()
    try:
        chats = db.query(models.Chat).filter(
            models.Chat.user_id == current_user.id
        ).order_by(models.Chat.id.desc()).limit(50).all()
        
        return {
            "total": len(chats),
            "chats": [
                {
                    "id": c.id,
                    "message": c.message,
                    "response": c.response
                } for c in chats
            ]
        }
    finally:
        db.close()