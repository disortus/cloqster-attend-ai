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

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"