from databases.postgres import database
from fastapi import HTTPException


async def get_schedule_for_student(student_id: int) -> list:
    async with database.pool.acquire() as conn:

        # Проверяем, что студент существует и является студентом
        user = await conn.fetchrow("""
            SELECT id, role 
            FROM Users
            WHERE id = $1
        """, student_id)

        if not user or user["role"] != "student":
            raise HTTPException(403, "Только студент может просматривать расписание")

        # Находим группу студента
        group_id = await conn.fetchrow("""
            SELECT group_id 
            FROM Students_Groups 
            WHERE student_id = $1
        """, student_id)

        if not group_id:
            raise HTTPException(404, "Группа студента не найдена")

        group_id = group_id["group_id"]

        # Получаем расписание
        schedule = await conn.fetch("""
            SELECT 
                g.group_name,
                s.weekday,
                s.start_time,
                s.end_time,
                subj.subj_name,
                u.fullname AS teacher_fullname,
                a.aud_number,
                s.valid_from,
                s.valid_to
            FROM Schedules s
            JOIN Groups g ON s.group_id = g.id
            JOIN Users u ON s.teacher_id = u.id
            JOIN Subjects subj ON s.subj_id = subj.id
            JOIN Audience a ON s.aud_id = a.id
            WHERE s.group_id = $1
            ORDER BY s.weekday, s.start_time
        """, group_id)

        if not schedule:
            raise HTTPException(404, "Расписание отсутствует")

        return [dict(row) for row in schedule]

async def get_lessons():
    async with database.pool.acquire() as conn:
        rows = conn.fetch("SELECT * FROM Lessons")
        # if not rows:
        #    raise HTTPException(400, "занятия не найдены")
        return [dict(r) for r in rows] if rows else []