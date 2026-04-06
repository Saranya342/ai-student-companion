from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
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