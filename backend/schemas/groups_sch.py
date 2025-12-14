from pydantic import BaseModel

class Spec(BaseModel):
     qua_name: str
     lang: str
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
     
