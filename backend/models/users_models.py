from schemas.users_sch import Token, UserLogin
from auth.security import verify_password
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from databases.postgres import database
from auth.utils import create_token


reuseable_oauth = OAuth2PasswordBearer(tokenUrl="/login",scheme_name="JWT")

async def login_user(data: UserLogin):
    async with database.pool.acquire() as conn:
        user = await conn.fetchrow("""
            SELECT * FROM Users WHERE email = $1
        """, data.email)

        if not user or not verify_password(data.password, user["password"]):
            raise HTTPException(400, "Неверный логин или пароль")

        token = create_token({"id": user["id"], "role": user["role"]})
        return Token(access_token=token)


