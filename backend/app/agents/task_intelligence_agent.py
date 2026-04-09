import requests
import os
from typing import List, Dict
import logging
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class TaskIntelligenceAgent:
    """
    Handles:
    - Extracting tasks from chat
    - Adding to planner
    - Deadline understanding
    """
    
    def __init__(self):
        self.extraction_prompt = """Extract ONLY tasks, assignments, or exams from this message.

Message: "{message}"

For each task:
- title: brief description
- due_date: "YYYY-MM-DD" or "today"/"tomorrow"/"next week"
- priority: "high"/"medium"/"low"
- category: "academic"/"personal"/"other"

Return JSON array. If no tasks, return [].

Example:
Input: "I have math exam tomorrow and project due Friday"
Output: [{{"title": "Math exam", "due_date": "tomorrow", "priority": "high", "category": "academic"}}]
"""
    
    def extract_tasks(self, message: str) -> List[Dict]:
        """Extract tasks using Groq"""
        
        if not self._has_task_keywords(message):
            return []
        
        prompt = self.extraction_prompt.format(message=message)
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        body = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 400,
            "temperature": 0.2
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
            
            tasks = json.loads(response_text.strip())
            logger.info(f"📋 Extracted {len(tasks)} tasks")
            return tasks if isinstance(tasks, list) else []
            
        except Exception as e:
            logger.error(f"❌ Task extraction failed: {e}")
            return []
    
    def _has_task_keywords(self, message: str) -> bool:
        """Quick check for task keywords"""
        keywords = [
            "task", "homework", "assignment", "exam", "test",
            "project", "deadline", "due", "submit", "presentation"
        ]
        return any(kw in message.lower() for kw in keywords)
    
    def parse_relative_date(self, date_str: str) -> str:
        """Convert relative dates to YYYY-MM-DD"""
        
        today = datetime.now()
        
        if date_str.lower() == "today":
            return today.strftime("%Y-%m-%d")
        elif date_str.lower() == "tomorrow":
            return (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "next week" in date_str.lower():
            return (today + timedelta(weeks=1)).strftime("%Y-%m-%d")
        
        return date_str  # Return as-is if already formatted
    
    def add_to_planner(self, db, user_id: int, tasks: List[Dict]):
        """Auto-add extracted tasks to planner"""
        
        from app.database.models import Task
        
        added_count = 0
        for task in tasks:
            try:
                due_date = self.parse_relative_date(task.get("due_date", ""))
                
                new_task = Task(
                    title=task["title"],
                    due_date=due_date,
                    priority=task.get("priority", "medium"),
                    user_id=user_id,
                    is_completed=False
                )
                db.add(new_task)
                added_count += 1
                
            except Exception as e:
                logger.error(f"Failed to add task: {e}")
        
        db.commit()
        logger.info(f"✅ Added {added_count} tasks to planner")
        return added_count


# Global instance
task_intelligence_agent = TaskIntelligenceAgent()