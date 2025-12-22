from fastapi import APIRouter
from app.database import get_db
from app.repositories.detection_repository import DetectionRepository

router = APIRouter()

@router.get("/species")
async def get_species_stats():
    async with get_db() as db:
        repo = DetectionRepository(db)
        stats = await repo.get_species_counts()
        return stats
