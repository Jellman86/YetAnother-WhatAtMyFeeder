from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from app.config import settings

router = APIRouter()

class SettingsUpdate(BaseModel):
    frigate_url: str = Field(..., min_length=1, description="Frigate instance URL")
    mqtt_server: str = Field(..., min_length=1, description="MQTT server hostname")
    mqtt_port: int = Field(1883, ge=1, le=65535, description="MQTT server port")
    mqtt_auth: bool = Field(False, description="Enable MQTT authentication")
    mqtt_username: Optional[str] = Field(None, description="MQTT username")
    mqtt_password: Optional[str] = Field(None, description="MQTT password")
    classification_threshold: float = Field(..., ge=0.0, le=1.0, description="Classification confidence threshold (0-1)")
    cameras: List[str] = Field(default_factory=list, description="List of cameras to monitor")

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
        "mqtt_port": settings.frigate.mqtt_port,
        "mqtt_auth": settings.frigate.mqtt_auth,
        "mqtt_username": settings.frigate.mqtt_username,
        "mqtt_password": settings.frigate.mqtt_password,
        "classification_threshold": settings.classification.threshold,
        "cameras": settings.frigate.camera
    }

@router.post("/settings")
async def update_settings(update: SettingsUpdate):
    settings.frigate.frigate_url = update.frigate_url
    settings.frigate.mqtt_server = update.mqtt_server
    settings.frigate.mqtt_port = update.mqtt_port
    settings.frigate.mqtt_auth = update.mqtt_auth
    if update.mqtt_username is not None:
        settings.frigate.mqtt_username = update.mqtt_username
    if update.mqtt_password is not None:
        settings.frigate.mqtt_password = update.mqtt_password
    
    settings.frigate.camera = update.cameras
    settings.classification.threshold = update.classification_threshold
    settings.save()
    return {"status": "updated"}