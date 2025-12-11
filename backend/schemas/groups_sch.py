from pydantic import BaseModel

class Spec(BaseModel):
     qua_name: str
     lang: str
     spec_name: str

class Group(Spec):
     group_name: str