from pydantic import BaseModel

class UserReg(BaseModel):
    login: str
    password: str
    role: str 
    fullname: str

class UserOut(BaseModel):
    login: str
    fullname: str
    role: str


class UserLogin(BaseModel):
    login: str
    password: str    

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"