from databases.postgres import database
from datetime import datetime
from fastapi import HTTPException

async def update_attendance_from_camera(aud_id: int, student_id: int, timestamp: datetime):
    async with database.pool.acquire() as conn:
        # Находим текущий урок по аудитории и времени
        now_time = timestamp.time()
        today = timestamp.date()

        lesson = await conn.fetchrow("""
            SELECT l.id AS lesson_id, s.group_id
            FROM Lessons l
            JOIN Schedules s ON l.schedule_id = s.id
            WHERE s.aud_id = $1
              AND l.lesson_date = $2
              AND s.start_time <= $3
              AND s.end_time >= $3
              AND l.status = 'planned'  -- или 'ongoing', как у тебя
        """, aud_id, today, now_time)

        if not lesson:
            raise HTTPException(status_code=404, detail="Нет текущего урока для этой аудитории")

        lesson_id = lesson["lesson_id"]
        group_id = lesson["group_id"]

        # Обновляем или создаём запись в Attends
        attend = await conn.fetchrow("""
            SELECT status, come_at FROM Attends
            WHERE lesson_id = $1 AND student_id = $2
        """, lesson_id, student_id)

        if attend and attend["status"] == "present":
            # Уже отмечен — просто обновляем last_seen
            await conn.execute("""
                UPDATE Attends SET last_seen = $1 WHERE lesson_id = $2 AND student_id = $3
            """, timestamp, lesson_id, student_id)
        else:
            # Первый раз видим — отмечаем как present
            await conn.execute("""
                UPDATE Attends
                SET status = 'present',
                    come_at = COALESCE(come_at, $1),
                    last_seen = $1,
                    marked_by = 'camera'
                WHERE lesson_id = $2 AND student_id = $3
            """, timestamp, lesson_id, student_id)

        # Возвращаем данные для уведомления
        student_info = await conn.fetchrow("""
            SELECT u.full_name FROM Users u WHERE id = $1
        """, student_id)

        return {
            "lesson_id": lesson_id,
            "group_id": group_id,
            "student_id": student_id,
            "student_name": student_info["full_name"] if student_info else "Unknown",
            "timestamp": timestamp.isoformat(),
            "action": "present" if not attend or attend["status"] != "present" else "seen"
        }