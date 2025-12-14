import jwt
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, Depends
from databases.postgres import database

secret_key = "your-secret-key"
ALGORITHM = "HS256"

def create_token(payload: dict):
    token_payload = {
        **payload,
        "exp": datetime.now() + timedelta(hours=1)
    }
    return jwt.encode(token_payload, secret_key, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(401, "Not authenticated")

    payload = decode_token(token)

    user_id = payload.get("id")
    role = payload.get("role")

    if not user_id or not role:
        raise HTTPException(401, "Invalid token payload")

    async with database.pool.acquire() as conn:
        user = await conn.fetchrow("""
            SELECT id, email, role, fullname
            FROM Users
            WHERE id = $1
        """, user_id)

    if not user:
        raise HTTPException(401, "User not found")

    return {
        "id": user["id"],
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