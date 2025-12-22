import json
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field

CONFIG_PATH = Path("config.json")

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
                # If we want env vars to override file (e.g. for docker secrets), we might need a different strategy.
                # For this app (interactive settings), file usually wins.
                return cls(**data)
            except Exception as e:
                print(f"Failed to load config from {CONFIG_PATH}: {e}")
                return cls()
        return cls()

settings = Settings.load()
