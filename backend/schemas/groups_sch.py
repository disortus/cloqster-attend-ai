from pydantic import BaseModel
from enum import Enum

class Qualification(str, Enum):
     bacalvr = "bacalvr"
     magistr = "magistr"
     doctor = "doctor"
     college = "college"

class Lang(str, Enum):
     ru = "rus"
     kz = "kaz"
     en = "eng"

class Spec(BaseModel):
     qua_name: Qualification
     lang: Lang
     spec_name: str

class Group(Spec):
     group_name: str
     fullname: str  # curator's fullname

class GroupDelete(BaseModel):
     group_name: str

class GroupCurUpdate(GroupDelete):
     fullname: str

class GroupUpdate(BaseModel):
     group_name: str
     new_group_name: str

class GroupStdUpdate(BaseModel):
     group_name: str
     fullname: str
     new_group_name: str
     
