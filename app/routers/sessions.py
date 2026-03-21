# /sessions endpoints

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
import httpx

from app.database import get_db
from app.models import Session, Question
from app.services.trivia_client import fetch_questions

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", status_code=201)
async def create_session(
    amount: int = 10,
    category: int = None,
    difficulty: str = None,
    db: DBSession = Depends(get_db),
):
    try:
        raw_questions = await fetch_questions(amount=amount, category=category, difficulty=difficulty)
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="Open Trivia DB is unavailable")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    session = Session(
        total_questions=len(raw_questions),
    )
    db.add(session)
    db.flush()

    for index, q in enumerate(raw_questions):
        question = Question(
            session_id=session.session_id,
            question_text=q["question_text"],
            correct_answer=q["correct_answer"],
            options=q["options"],
            order_index=index,
        )
        db.add(question)

    db.commit()
    db.refresh(session)

    return {"session_id": session.session_id}


@router.get("/{session_id}")
def get_session(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session.session_id,
        "status": session.status,
        "score": session.score,
        "total_questions": session.total_questions,
        "current_question_index": session.current_question_index,
    }
