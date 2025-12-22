from pydantic import BaseModel
from datetime import datetime

class Detection(BaseModel):
    id: int | None = None
    detection_time: datetime
    detection_index: int
    score: float
    display_name: str
    category_name: str
    frigate_event: str
    camera_name: str

class DetectionResponse(Detection):
    common_name: str | None = None

class FrigateEvent(BaseModel):
    id: str
    camera: str
    label: str
    start_time: float
    top_score: float | None = None
    false_positive: bool | None = None
