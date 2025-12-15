from pydantic import BaseModel
from enum import Enum



class Subject(BaseModel):
    subj_name: str
    spec_name: str