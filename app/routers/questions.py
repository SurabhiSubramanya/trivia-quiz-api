# /question + /answer endpoints

from fastapi import APIRouter, HTTPException
import httpx

from app.services.trivia_client import fetch_categories

router = APIRouter(tags=["questions"])


@router.get("/categories")
async def get_categories():
    try:
        categories = await fetch_categories()
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="Open Trivia DB is unavailable")

    return {"categories": categories}
