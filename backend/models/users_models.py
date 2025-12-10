from schemas.users_sch import UserReg, Token, UserLogin, UserOut
from auth.security import hash_password, verify_password
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from databases.postgres import database
from pydantic import ValidationError
from auth.utils import create_token
from datetime import datetime
from jwt import PyJWTError
from typing import List
import jwt

reuseable_oauth = OAuth2PasswordBearer(tokenUrl="/login",scheme_name="JWT")

async def login_user(data: UserLogin):
    async with database.pool.acquire() as conn:
        user = await conn.fetchrow("""
            SELECT * FROM Users WHERE login = $1
        """, data.login)

        if not user:
            raise HTTPException(400, "Неверный логин или пароль")

        if not verify_password(data.password, user["password"]):
            raise HTTPException(400, "Неверный логин или пароль")
        print(user["id"])
        token = create_token({"id": user["id"]})
        return Token(access_token=token)

async def get_users() -> List[UserOut]:
    query = "SELECT fullname, login FROM Users"
    async with database.pool.acquire() as connection:
        rows = await connection.fetch(query)
        # users = [Users(login=record["login"], fullname=record["fullname"]) for record in rows]
        return rows # users

async def reg_user(data: UserReg):
    async with database.pool.acquire() as conn:
        try:
            user = await conn.fetchrow("""
                INSERT INTO Users (login, password, fullname, role)
                VALUES ($1, $2, $3, $4)
                RETURNING login, fullname, role
            """,
            data.login,
            hash_password(data.password),
            data.fullname,
            data.role)
        except Exception as e:
            print(e)
            raise HTTPException(400, "Такой логин уже существует")

        return UserOut(**dict(user))

async def get_current_user(token: str = Depends(reuseable_oauth)) -> UserOut:
    try:
        payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
        user_id: int = payload.get("user_id")

        if datetime.fromtimestamp(user_id.exp) < datetime.now():
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except(PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async with database.pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT id, login, fullname, role FROM Users WHERE id = $1",
                user_id
            )


    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return UserOut(**user)
