from pydantic import BaseModel
from pydantic import EmailStr

class UserReg(BaseModel):
    email: EmailStr
    password: str
    role: str 
    fullname: str
    

class UserOut(BaseModel):
    email: EmailStr
    fullname: str
    role: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str    

class UserName(BaseModel):
    fullname: str

class StdGroup(UserName):
    group_name: str

class UserDelete(BaseModel):
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"