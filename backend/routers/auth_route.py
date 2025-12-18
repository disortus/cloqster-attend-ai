from schemas.users_sch import UserLogin, Token, UserOut
from fastapi import APIRouter, Depends, Response
from models import users_models
from auth import utils

auth_router = APIRouter(tags=["auth"])

@auth_router.post("/login")
async def login_user(data: UserLogin, response: Response) -> dict:
    token, user = await users_models.login_user(data)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=60 * 60,  # 1 час
        path="/",
        samesite="lax",
        secure=False  # True на HTTPS
    )
    return {"token": token,
            "user": user}


@auth_router.post("/logout")
async def logout(response: Response) -> dict:
    response.delete_cookie("access_token", path="/")
    return {"msg": "logged out"}

@auth_router.get("/me", response_model=UserOut)
async def get_current_user_info(current_user=Depends(utils.get_current_user)) -> UserOut:
    return current_user

@auth_router.post("/recognize", response_model=dict)
async def recognize(data: dict) -> dict:
    await users_models.accept_req(data)

@auth_router.put("/recognize", response_model=dict)
async def updt_recognize(data: dict) -> dict:
    await users_models.upd_req(data)