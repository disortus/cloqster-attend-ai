from schemas.users_sch import UserLogin, Token, UserOut
from fastapi import APIRouter, Depends
from models import users_models
from auth import utils
auth_router = APIRouter(tags=["auth"])

@auth_router.post("/login", response_model=Token)
async def login_user(data: UserLogin):
    return await users_models.login_user(data)

@auth_router.post("/me", response_model=UserOut)
async def get_current_user_info(current_user=Depends(utils.get_current_user)):
    return current_user