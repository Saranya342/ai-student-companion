from sqlalchemy.orm import Session
from app.database import models
from app.services.websocket_manager import websocket_manager
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class NotificationAgent:
    def check_and_send_notifications(self, db: Session):
        """
        Main function to check for all notifiable events.
        This will be run by the background scheduler.
        """
        logger.info("⏰ Running notification check...")
        users = db.query(models.User).all()
        for user in users:
            self._check_for_due_tasks(db, user)
            # Add more checks here in the future (e.g., bag reminders, exam reminders)

    def _check_for_due_tasks(self, db: Session, user: models.User):
        """Checks for tasks due within the next 24 hours."""
        tomorrow = datetime.utcnow() + timedelta(days=1)

        # Find tasks that are due soon and not completed
        due_soon_tasks = db.query(models.Task).filter(
            models.Task.user_id == user.id,
            models.Task.is_completed == False,
            models.Task.due_date <= str(tomorrow.date()) # Simple string comparison
        ).all()

        for task in due_soon_tasks:
            try:
                # IMPORTANT: Check if we already sent a notification for this task
                existing_notification = db.query(models.Notification).filter(
                    models.Notification.user_id == user.id,
                    models.Notification.title.like(f"%{task.title}%") # Simple check
                ).first()

                if not existing_notification:
                    logger.info(f"🔥 Found urgent task for user {user.id}: {task.title}")
                    
                    title = f"Task Due Soon: {task.title}"
                    message = f"Hey! Just a heads-up, your task '{task.title}' is due on {task.due_date}. You got this! 💪"
                    priority = "high" if task.priority == "high" else "normal"

                    # 1. Save notification to the database
                    new_notification = models.Notification(
                        title=title,
                        message=message,
                        type="task",
                        priority=priority,
                        user_id=user.id
                    )
                    db.add(new_notification)
                    db.commit()
                    db.refresh(new_notification)

                    # 2. Send real-time push notification via WebSocket
                    notification_payload = {
                        "id": new_notification.id,
                        "title": title,
                        "message": message,
                        "priority": priority,
                        "type": "task",
                        "created_at": new_notification.created_at.isoformat()
                    }
                    # Use asyncio.run if calling from a sync function context
                    import asyncio
                    asyncio.run(websocket_manager.send_personal_message(user.id, notification_payload))
            except Exception as e:
                logger.error(f"Error processing task notification for user {user.id}: {e}")
                db.rollback()


# Global instance
notification_agent = NotificationAgent()