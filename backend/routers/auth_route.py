from schemas.users_sch import UserLogin, Token, UserReg, UserOut
from fastapi import APIRouter, Depends
from models import users_models

auth_router = APIRouter(tags=["auth"])



@auth_router.post("/login", response_model=Token)
async def login_user(data: UserLogin):
    return await users_models.login_user(data)


@auth_router.get("/me", response_model=UserOut)
async def me(current: UserOut = Depends(users_models.get_current_user)):
    return current
