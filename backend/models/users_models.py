from schemas.users_sch import UserLogin
from auth.security import verify_password
from fastapi import HTTPException
from databases.postgres import database
from auth.utils import create_token


async def login_user(data: UserLogin):
    async with database.pool.acquire() as conn:
        user = await conn.fetchrow("""
            SELECT id, email, password, role, fullname
            FROM Users
            WHERE email = $1
        """, data.email)

        if not user or not verify_password(data.password, user["password"]):
            raise HTTPException(400, "Неверный логин или пароль")

        token = create_token({
            "id": user["id"],
            "role": user["role"]
        })

        return token, {
            "email": user["email"],
            "fullname": user["fullname"],
            "role": user["role"]
        }

