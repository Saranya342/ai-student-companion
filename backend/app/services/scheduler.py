from apscheduler.schedulers.background import BackgroundScheduler
from app.database.connection import SessionLocal
from app.agents.notification_agent import notification_agent

scheduler = BackgroundScheduler(daemon=True)

def run_notification_checks():
    """Function to be executed by the scheduler."""
    db = SessionLocal()
    try:
        notification_agent.check_and_send_notifications(db)
    finally:
        db.close()

def start_scheduler():
    """Starts the scheduler and adds the job."""
    # Run the check every 5 minutes
    scheduler.add_job(run_notification_checks, 'interval', minutes=5)
    scheduler.start()
    print("🚀 Background scheduler started. Will check for notifications every 5 minutes.")