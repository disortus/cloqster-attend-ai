from pydantic import BaseModel
from enum import Enum

class AudType(str, Enum):
    clas = "class"
    lab = "lab"
    computer_class = "computer_class"

class AudSchema(BaseModel):
    aud_number: str
    build: str
    aud_type: AudType