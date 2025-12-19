from databases.postgres import database
from fastapi import HTTPException

async def get_attends_for_group(teacher_id: int):
    async with database.pool.acquire() as conn:
        # 1) находим группу, которую ведёт учитель
        group_data = await conn.fetchrow("""
            SELECT g.id, g.name
            FROM Schedules s
            JOIN Groups g ON g.id = s.group_id
            WHERE s.teacher_id = $1
            LIMIT 1
        """, teacher_id)

        if not group_data:
            raise HTTPException(404, "Teacher has no assigned group")

        group_id = group_data["id"]

        # 2) получаем все уроки этой группы
        lessons = await conn.fetch("""
            SELECT l.id AS lesson_id, l.lesson_date, sub.name AS subject
            FROM Lessons l
            JOIN Schedules s ON s.id = l.schedule_id
            JOIN Subjects sub ON sub.id = l.subj_id
            WHERE s.group_id = $1
            ORDER BY l.lesson_date DESC
        """, group_id)

        result = {
            "group_id": group_id,
            "group": group_data["name"],
            "lessons": []
        }

        # 3) для каждого урока — посещаемость
        for lesson in lessons:
            attends = await conn.fetch("""
                SELECT a.student_id,
                       u.fullname,
                       a.status,
                       a.come_at,
                       a.mark_source,
                       a.marked_by
                FROM Attends a
                JOIN Users u ON u.id = a.student_id
                WHERE a.lesson_id = $1
            """, lesson["lesson_id"])

            result["lessons"].append({
                "lesson_id": lesson["lesson_id"],
                "date": lesson["lesson_date"],
                "subject": lesson["subject"],
                "attends": [
                    {
                        "student_id": r["student_id"],
                        "fullname": r["fullname"],
                        "status": r["status"],
                        "come_at": r["come_at"],
                        "mark_source": r["mark_source"],
                        "marked_by": r["marked_by"]
                    }
                    for r in attends
                ]
            })

        return result

async def update_attend_status(lesson_id: int, student_id: int, status: str, teacher_id: int):
    async with database.pool.acquire() as conn:

        # 1) Проверяем, есть ли такая запись
        attend = await conn.fetchrow("""
            SELECT id, status, mark_source, marked_by
            FROM Attends
            WHERE lesson_id = $1 AND student_id = $2
        """, lesson_id, student_id)

        if not attend:
            raise HTTPException(404, "Attend not found")

        # 2) Обновляем
        updated = await conn.fetchrow("""
            UPDATE Attends
            SET status = $1,
                mark_source = 'teacher',
                marked_by = $2
            WHERE lesson_id = $3 AND student_id = $4
            RETURNING id, lesson_id, student_id, status, come_at, mark_source, marked_by
        """, status, teacher_id, lesson_id, student_id)

        return {
            "id": updated["id"],
            "lesson_id": updated["lesson_id"],
            "student_id": updated["student_id"],
            "status": updated["status"],
            "mark_source": updated["mark_source"],
            "marked_by": updated["marked_by"],
            "come_at": updated["come_at"],
        }

async def get_lessons():
    async with database.pool.acquire() as conn:
        rows = conn.fetch("SELECT * FROM Lessons")
        # if not rows:
        #    raise HTTPException(400, "занятия не найдены")
        return [dict(r) for r in rows] if rows else []
        