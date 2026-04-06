from fastapi import FastAPI
from app.database.connection import engine
from app.database import models
from app.api import users
from app.routes import chat, bag, planner

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(bag.router, prefix="/bag", tags=["Bag Checker"])
app.include_router(planner.router, prefix="/planner", tags=["Planner"])

@app.get("/")
def home():
    return {"message": "AI Student Companion Backend Running ✅"}