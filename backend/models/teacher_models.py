from databases.postgres import database
from fastapi import HTTPException
from ws.attends_ws import broadcast
from ws.redis_pubsub import publish_attend

async def get_attends_for_lesson(teacher_id: int, lesson_id: int):
    async with database.pool.acquire() as conn:

        # проверяем, что учитель ведет этот урок
        lesson = await conn.fetchrow("""
            SELECT id FROM Lessons 
            WHERE id = $1 AND teacher_id = $2
        """, lesson_id, teacher_id)

        if not lesson:
            raise HTTPException(403, "Нет доступа к уроку")

        attends = await conn.fetch("""
            SELECT A.id, A.student_id, A.status, A.come_at, A.mark_source, 
                   A.marked_by, U.fullname AS student_name
            FROM Attends A
            JOIN Users U ON A.student_id = U.id
            WHERE A.lesson_id = $1
        """, lesson_id)

        return [dict(a) for a in attends]


async def teacher_update_attend(teacher_id: int, attend_id: int, new_status: str):
    async with database.pool.acquire() as conn:

        attend = await conn.fetchrow("""
            SELECT lesson_id FROM Attends WHERE id = $1
        """, attend_id)

        if not attend:
            raise HTTPException(404, "Attend не найден")

        # фиксируем ручную правку
        await conn.execute("""
            UPDATE Attends 
            SET status = $1, mark_source = 'teacher', marked_by = $2
            WHERE id = $3
        """, new_status, teacher_id, attend_id)

        event = {
            "type": "attend_updated",
            "attend_id": attend_id,
            "lesson_id": attend["lesson_id"],
            "status": new_status,
            "source": "teacher",
            "teacher_id": teacher_id
        }

        await publish_attend(event)

        return {"ok": True}

async def get_lessons():
    async with database.pool.acquire() as conn:
        rows = conn.fetch("SELECT * FROM Lessons")
        # if not rows:
        #    raise HTTPException(400, "занятия не найдены")
        return [dict(r) for r in rows] if rows else []