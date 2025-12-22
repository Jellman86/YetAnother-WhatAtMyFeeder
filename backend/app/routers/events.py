from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.database import get_db
from app.models import DetectionResponse
from app.repositories.detection_repository import DetectionRepository

router = APIRouter()

@router.get("/events", response_model=List[DetectionResponse])
async def get_events(
    limit: int = Query(default=50, ge=1, le=500, description="Number of events to return"),
    offset: int = Query(default=0, ge=0, description="Number of events to skip")
):
    async with get_db() as db:
        repo = DetectionRepository(db)
        events = await repo.get_all(limit=limit, offset=offset)
        return events
