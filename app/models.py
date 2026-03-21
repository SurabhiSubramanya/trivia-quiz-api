# ORM table definitions
# app/models.py

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, JSON, Boolean
from sqlalchemy.orm import DeclarativeBase
import enum

# --- Base class all models will inherit from ---
class Base(DeclarativeBase):
    pass

# --- Enum for session status ---
class SessionState(str, enum.Enum):
    active = "active"
    completed = "completed"
    abandoned = "abandoned"

# --- Session model ---
class Session(Base):
    __tablename__ = "sessions"

    # Format: 
    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(Enum(SessionState), nullable=False, default=SessionState.active)
    score = Column(Integer, nullable=False, default=0)
    total_questions = Column(Integer, nullable=False)
    current_question_index = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    # when session created, no relevant completed time, so allow NULL
    completed_at = Column(DateTime, nullable=True)


# --- Question model ---
class Question(Base):
    __tablename__ = "questions"

    question_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.session_id"), nullable=False)
    question_text = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)
    options = Column(JSON, nullable=False)          # shuffled list of all choices
    order_index = Column(Integer, nullable=False)   # position in the quiz (0-based)


# --- Answer model ---
class Answer(Base):
    __tablename__ = "answers"

    answer_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.session_id"), nullable=False)
    question_id = Column(String, ForeignKey("questions.question_id"), nullable=False)
    submitted_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    answered_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))