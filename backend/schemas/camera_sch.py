from pydantic import BaseModel
from datetime import datetime

class CameraDetection(BaseModel):
    aud_id: int
    student_id: int
    timestamp: datetime