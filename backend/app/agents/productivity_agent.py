import requests
import os
from typing import Dict, Optional, List
import logging
import json
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class ProductivityAgent:
    """
    Handles:
    - Procrastination detection
    - Micro-task splitting
    - Deadline nudging
    """
    
    def __init__(self):
        self.micro_task_prompt = """You are a productivity coach.

Break this task into 3-5 small micro-tasks (15-30 min each).

Task: {task_description}

Return ONLY a JSON array:
[
  {{"step": 1, "task": "Review notes (15 min)", "time": "15 min"}},
  {{"step": 2, "task": "Practice 3 problems (25 min)", "time": "25 min"}}
]
"""
        
        # Procrastination keywords
        self.procrastination_keywords = [
            "later", "tomorrow", "not now", "lazy", "don't feel like",
            "procrastinating", "putting off", "delaying", "scrolling",
            "distracted", "can't focus", "youtube", "instagram", "netflix"
        ]
    
    def detect_procrastination(self, message: str) -> Dict:
        """Check if user is procrastinating"""
        
        message_lower = message.lower()
        matched_keywords = [kw for kw in self.procrastination_keywords if kw in message_lower]
        
        is_procrastinating = len(matched_keywords) > 0
        severity = "high" if len(matched_keywords) >= 2 else "medium" if matched_keywords else "none"
        
        return {
            "is_procrastinating": is_procrastinating,
            "severity": severity,
            "matched_keywords": matched_keywords
        }
    
    def should_activate(self, message: str, emotion: str) -> bool:
        """Check if Productivity Agent is needed"""
        
        overwhelm_keywords = [
            "huge", "overwhelming", "too much", "don't know where to start",
            "so much", "can't handle", "massive", "difficult", "stuck"
        ]
        
        message_lower = message.lower()
        has_overwhelm = any(kw in message_lower for kw in overwhelm_keywords)
        is_stressed = emotion in ["stressed", "anxious", "tired"]
        is_procrastinating = self.detect_procrastination(message)["is_procrastinating"]
        
        return has_overwhelm or is_stressed or is_procrastinating
    
    def split_task(self, task_description: str) -> Optional[Dict]:
        """Break down a task into micro-tasks"""
        
        prompt = self.micro_task_prompt.format(task_description=task_description)
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        body = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.5
        }
        
        try:
            res = requests.post(GROQ_URL, headers=headers, json=body, timeout=15)
            res.raise_for_status()
            response_text = res.json()["choices"][0]["message"]["content"]
            
            # Strip markdown
            if "```" in response_text:
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            micro_tasks = json.loads(response_text.strip())
            
            if not isinstance(micro_tasks, list):
                return None
            
            logger.info(f"🎯 Generated {len(micro_tasks)} micro-tasks")
            
            return {
                "main_task": task_description,
                "micro_tasks": micro_tasks
            }
            
        except Exception as e:
            logger.error(f"❌ Productivity agent failed: {e}")
            return None
    
    def get_deadline_nudge(self, due_date: str) -> str:
        """Generate deadline reminder message"""
        
        from datetime import datetime
        
        try:
            # Parse due date
            if due_date.lower() in ["today", "tomorrow", "next week"]:
                return f"⏰ Your deadline is {due_date.upper()}! Start now with just 5 minutes."
            
            due = datetime.strptime(due_date, "%Y-%m-%d")
            days_left = (due - datetime.now()).days
            
            if days_left <= 0:
                return "🚨 URGENT: This task is DUE TODAY!"
            elif days_left == 1:
                return "⏰ Tomorrow deadline! Quick 15-minute start?"
            elif days_left <= 3:
                return f"📅 Only {days_left} days left. Break it into steps?"
            else:
                return f"📅 {days_left} days remaining. Plan ahead!"
                
        except Exception:
            return "📅 Deadline approaching. Start early!"
    
    def get_motivational_nudge(self) -> str:
        """Generate anti-procrastination message"""
        
        nudges = [
            "💪 Just 5 minutes. That's all. Start now!",
            "🚀 One small step. Let's do this!",
            "⏰ Future you will thank present you. Begin!",
            "🎯 Focus on just the first tiny step.",
            "🔥 You've got this! Start with 2 minutes."
        ]
        
        import random
        return random.choice(nudges)


# Global instance
productivity_agent = ProductivityAgent()