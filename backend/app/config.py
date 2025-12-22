import json
import os
import structlog
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field

log = structlog.get_logger()

# Use /config directory for persistent config (matches Docker volume mount)
CONFIG_PATH = Path("/config/config.json")

class FrigateSettings(BaseModel):
    frigate_url: str = Field(..., description="URL of the Frigate instance")
    main_topic: str = "frigate"
    camera: list[str] = Field(default_factory=list, description="List of cameras to monitor")
    mqtt_server: str = "mqtt"
    mqtt_port: int = 1883
    mqtt_auth: bool = False
    mqtt_username: str = ""
    mqtt_password: str = ""

class ClassificationSettings(BaseModel):
    model: str = "model.tflite"
    threshold: float = 0.7

class Settings(BaseSettings):
    frigate: FrigateSettings
    classification: ClassificationSettings = ClassificationSettings()
    
    # General app settings
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(env_nested_delimiter='__', env_file='.env', extra='ignore')

    def save(self):
        with open(CONFIG_PATH, 'w') as f:
            f.write(self.model_dump_json(indent=2))
            
    @classmethod
    def load(cls):
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, 'r') as f:
                    data = json.load(f)
                # We merge with env vars by creating an instance. 
                # Pydantic prefers init args > env vars > defaults.
                # So passing the file data as kwargs overrides env vars. 
                # FIX: If specific MQTT env vars are present, remove them from 'data' 
                # so Pydantic uses the env var value instead of the file value.
                if 'frigate' in data:
                    if os.environ.get('FRIGATE__MQTT_SERVER'):
                        data['frigate'].pop('mqtt_server', None)
                    if os.environ.get('FRIGATE__MQTT_PORT'):
                        data['frigate'].pop('mqtt_port', None)
                    if os.environ.get('FRIGATE__MQTT_AUTH'):
                        data['frigate'].pop('mqtt_auth', None)
                    if os.environ.get('FRIGATE__MQTT_USERNAME'):
                        data['frigate'].pop('mqtt_username', None)
                    if os.environ.get('FRIGATE__MQTT_PASSWORD'):
                        data['frigate'].pop('mqtt_password', None)

                return cls(**data)
            except Exception as e:
                log.warning("Failed to load config from file, using defaults", path=str(CONFIG_PATH), error=str(e))
        # Return with default frigate settings - frigate_url is required
        return cls(frigate=FrigateSettings(frigate_url="http://frigate:5000"))

settings = Settings.load()
