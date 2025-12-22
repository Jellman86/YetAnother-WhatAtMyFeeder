from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.database import get_db
from app.models import DetectionResponse
from app.repositories.detection_repository import DetectionRepository

router = APIRouter()

@router.get("/events", response_model=List[DetectionResponse])
async def get_events(limit: int = 50, offset: int = 0):
    async with get_db() as db:
        repo = DetectionRepository(db)
        events = await repo.get_all(limit=limit, offset=offset)
        return events
