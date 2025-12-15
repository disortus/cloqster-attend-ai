from pydantic import BaseModel, EmailStr
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    curator = "curator"
    teacher = "teacher"
    student = "student"

class UserReg(BaseModel):
    email: EmailStr
    password: str
    role: UserRole
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