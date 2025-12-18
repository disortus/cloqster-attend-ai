from schemas.users_sch import UserLogin
from auth.security import verify_password
from fastapi import HTTPException
from databases.postgres import database
from auth.utils import create_token


async def login_user(data: UserLogin) -> dict:
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

async def accept_req(data: dict) -> dict:
    async with database.pool.acquire() as conn:
        lesson_id = await conn.fetchrow("""SELECT id FROM Lessons 
                                     WHERE schedele_id = $1""", data["schedule_id"])
        if not lesson_id:
            raise HTTPException(400, "урок не найден")
        mark_src = "system"
        await conn.fetchrow("""INSERT INTO Attends (lesson_id, student_id, status, come_at, mark_source)
                      VALUES ($1, $2, $3, $4, $5)""",lesson_id, data["id"], data["status"], data["time"], mark_src)
        return {"ok": True}

async def upd_req(data: dict) -> dict:
    async with database.pool.acquire() as conn:
        lesson_id = await conn.fetchrow("""UPDATE Attends SET status = $1
                                        WHERE status = $2 AND student_id = $3""", 
                                        data["status"], data["final_status"], data["id"])
