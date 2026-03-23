import logging
import json

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from sqlalchemy import text

from app.database import engine
from app.models import Base, Session, Question, Answer
from app.routers import sessions, questions
from app.middleware import RequestIDMiddleware, PrometheusMiddleware


def configure_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logging.root.setLevel(logging.INFO)
    logging.root.handlers = [handler]


configure_logging()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Trivia Quiz API")

app.add_middleware(RequestIDMiddleware)
app.add_middleware(PrometheusMiddleware)

app.mount("/metrics", make_asgi_app())

app.include_router(sessions.router)
app.include_router(questions.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/ready")
def readiness_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return JSONResponse(
            {"status": "not ready", "detail": str(e)},
            status_code=503,
        )
