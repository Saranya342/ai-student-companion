from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    chats = relationship("Chat", back_populates="user")
    bag_items = relationship("BagItem", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    memories = relationship("Memory", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    streaks = relationship("Streak", back_populates="user")  # ADD THIS
    motivational_memories = relationship("MotivationalMemory", back_populates="user")  # ADD THIS
    journal_entries = relationship("JournalEntry", back_populates="user") 
class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    response = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="chats")


class BagItem(Base):
    __tablename__ = "bag_items"

    id = Column(Integer, primary_key=True, index=True)
    day = Column(String)
    item_name = Column(String)
    is_checked = Column(String, default="false")
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="bag_items")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String, nullable=True)
    due_date = Column(String)
    priority = Column(String, default="medium")
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="tasks")


class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    embedding_id = Column(String, unique=True, nullable=True)  # nullable now
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="memories")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False)
    priority = Column(String, default="normal")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="notifications")

# Add to existing models.py

class Streak(Base):
    __tablename__ = "streaks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    streak_type = Column(String, nullable=False)  # "daily_highfive", "journal", "task"
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(DateTime(timezone=True))
    
    user = relationship("User", back_populates="streaks")


class MotivationalMemory(Base):
    __tablename__ = "motivational_memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    emoji = Column(String)  # "🎉", "🔥", "📚"
    memory_type = Column(String)  # "achievement", "milestone", "streak_unlock"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="motivational_memories")

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    entry_type = Column(String, nullable=False)  # "thought_parking", "future_letter", "reflection"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="journal_entries")
    