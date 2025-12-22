from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from app.config import settings

router = APIRouter()

class SettingsUpdate(BaseModel):
    frigate_url: str = Field(..., min_length=1, description="Frigate instance URL")
    mqtt_server: str = Field(..., min_length=1, description="MQTT server hostname")
    classification_threshold: float = Field(..., ge=0.0, le=1.0, description="Classification confidence threshold (0-1)")

    @field_validator('frigate_url')
    @classmethod
    def validate_frigate_url(cls, v: str) -> str:
        if not v.startswith(('http://', 'https://')):
            raise ValueError('frigate_url must start with http:// or https://')
        return v.rstrip('/')

@router.get("/settings")
async def get_settings():
    return {
        "frigate_url": settings.frigate.frigate_url,
        "mqtt_server": settings.frigate.mqtt_server,
        "classification_threshold": settings.classification.threshold
    }

@router.post("/settings")
async def update_settings(update: SettingsUpdate):
    settings.frigate.frigate_url = update.frigate_url
    settings.frigate.mqtt_server = update.mqtt_server
    settings.classification.threshold = update.classification_threshold
    settings.save()
    return {"status": "updated"}
