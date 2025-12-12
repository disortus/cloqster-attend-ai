import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from databases.postgres import database
from datetime import datetime, timedelta

secret_key = "your-secret-key"

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT"
)

def create_token(payload: dict):
    token_payload = {
        **payload,
        "exp": datetime.now() + timedelta(hours=1)
    }
    return jwt.encode(token_payload, secret_key, algorithm="HS256")


def decode_token(token: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
    except Exception:
        raise HTTPException(401, "Token error")


async def get_current_user(token: str = Depends(reuseable_oauth)):
    payload = decode_token(token)

    if "id" not in payload or "role" not in payload:
        raise HTTPException(401, "Invalid token payload")

    user_id = payload["id"]
    role = payload["role"]

    async with database.pool.acquire() as conn:
        user = await conn.fetchrow("""
            SELECT id, email, role, fullname
            FROM Users
            WHERE id = $1
        """, user_id)

    if not user:
        raise HTTPException(401, "User not found")

    return {
        "email": user["email"],
        "fullname": user["fullname"],
        "role": user["role"]
    }

def require_role(*allowed_roles):
    async def checker(user=Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            raise HTTPException(403, "Access denied")
        return user
    return checker
