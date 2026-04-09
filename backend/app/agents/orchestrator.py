from typing import Dict
from .emotion_vibe_agent import emotion_vibe_agent
from .task_intelligence_agent import task_intelligence_agent
from .productivity_agent import productivity_agent
from .memory_action_agent import memory_action_agent
import logging

logger = logging.getLogger(__name__)


class Orchestrator:
    """Routes user message to correct logic"""
    
    def route(self, user_id: int, message: str, db) -> Dict:
        """Main routing logic"""
        
        results = {
            "emotion_data": None,
            "tasks": [],
            "micro_tasks": None,
            "achievements": [],
            "actions": None,
            "agents_used": []
        }
        
        # 1. Check emotion + vibe
        emotion_data = emotion_vibe_agent.analyze(message)
        results["emotion_data"] = emotion_data
        results["agents_used"].append("emotion_vibe")
        
        # 2. Check for actions
        actions = memory_action_agent.analyze_for_actions(message)
        results["actions"] = actions
        results["agents_used"].append("memory_action")
        
        # 3. Extract tasks
        tasks = task_intelligence_agent.extract_tasks(message)
        if tasks:
            results["tasks"] = tasks
            results["agents_used"].append("task_intelligence")
        
        # 4. Get achievements if negative
        if emotion_data["is_negative"]:
            achievements = memory_action_agent.get_achievements(user_id, limit=3)
            results["achievements"] = achievements
        
        # 5. Productivity help
        if productivity_agent.should_activate(message, emotion_data["emotion"]):
            task_desc = tasks[0]["title"] if tasks else message
            micro_tasks = productivity_agent.split_task(task_desc)
            if micro_tasks:
                results["micro_tasks"] = micro_tasks
                results["agents_used"].append("productivity")
        
        logger.info(f"🤖 Agents used: {results['agents_used']}")
        return results


orchestrator = Orchestrator()