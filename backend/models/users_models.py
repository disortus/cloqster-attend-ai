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

# async def accept_req(data: dict) -> dict:
#     """
#     data = {
#         "schedule_id": int,
#         "student_id": int,
#         "status": str,
#         "time": "HH:MM:SS"
#     }
#     """
#     async with database.pool.acquire() as conn:

#         # 1) находим урок по schedule_id
#         lesson = await conn.fetchrow("""
#             SELECT id, schedule_id 
#             FROM Lessons
#             WHERE schedule_id = $1
#             ORDER BY lesson_date DESC
#             LIMIT 1
#         """, data["schedule_id"])

#         if not lesson:
#             raise HTTPException(400, "Урок не найден")

#         lesson_id = lesson["id"]

#         # 2) запись от камеры
#         result = await conn.fetchrow("""
#             INSERT INTO Attends (lesson_id, student_id, status, come_at, mark_source)
#             VALUES ($1, $2, $3, $4, 'system')
#             RETURNING *
#         """, lesson_id, data["student_id"], data["status"], data["time"])

#         # 3) получаем teacher_id для broadсast
#         teacher = await conn.fetchrow("""
#             SELECT teacher_id
#             FROM Schedules
#             WHERE id = $1
#         """, lesson["schedule_id"])

#         teacher_id = teacher["teacher_id"]

#         # 4) realtime notify
#         await broadcast.publish(
#             channel=f"teacher_{teacher_id}",
#             message={
#                 "type": "attend_created",
#                 "lesson_id": lesson_id,
#                 "student_id": result["student_id"],
#                 "status": result["status"],
#                 "mark_source": "system"
#             }
#         )

#         return {"ok": True}

# async def upd_req(data: dict) -> dict:
#     """
#     data = {
#         "lesson_id": int,
#         "student_id": int,
#         "status": str
#     }
#     """
#     async with database.pool.acquire() as conn:

#         # обновляем посещаемость
#         updated = await conn.fetchrow("""
#             UPDATE Attends
#             SET status = $1,
#                 mark_source = 'system',
#                 marked_by = NULL
#             WHERE lesson_id = $2
#               AND student_id = $3
#             RETURNING *
#         """, data["status"], data["lesson_id"], data["student_id"])

#         if not updated:
#             raise HTTPException(400, "Запись не найдена")

#         # узнаём teacher_id
#         teacher = await conn.fetchrow("""
#             SELECT s.teacher_id
#             FROM Lessons l
#             JOIN Schedules s ON s.id = l.schedule_id
#             WHERE l.id = $1
#         """, data["lesson_id"])

#         teacher_id = teacher["teacher_id"]

#         # realtime update event
#         await broadcast.publish(
#             channel=f"teacher_{teacher_id}",
#             message={
#                 "type": "attend_updated",
#                 "lesson_id": updated["lesson_id"],
#                 "student_id": updated["student_id"],
#                 "status": updated["status"],
#                 "mark_source": "system"
#             }
#         )

#         return {"ok": True}

