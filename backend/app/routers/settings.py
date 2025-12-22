from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.config import settings

router = APIRouter()

class SettingsUpdate(BaseModel):
    frigate_url: str
    mqtt_server: str
    classification_threshold: float

@router.get("/settings")
async def get_settings():
    return {
        "frigate_url": settings.frigate.frigate_url,
        "mqtt_server": settings.frigate.mqtt_server,
        "classification_threshold": settings.classification.threshold
    }

@router.post("/settings")
async def update_settings(update: SettingsUpdate):
    # In a real app this would persist to disk/env
    settings.frigate.frigate_url = update.frigate_url
    settings.frigate.mqtt_server = update.mqtt_server
    settings.classification.threshold = update.classification_threshold
    settings.save()
    return {"status": "updated"}
