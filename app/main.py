# FastAPI app entry point
# app/main.py

from fastapi import FastAPI
from app.database import engine
from app.models import Base, Session, Question, Answer
from app.routers import sessions, questions

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Trivia Quiz API")

app.include_router(sessions.router)
app.include_router(questions.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
