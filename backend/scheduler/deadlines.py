from datetime import datetime, timedelta
from databases.postgres import database
from scheduler.notifications import notify_deadline_passed

async def schedule_deadlines():
    async with database.pool.acquire() as conn:
        lessons = await conn.fetch("""
            SELECT Lessons.id, Lessons.lesson_date, Schedules.start_time
            FROM Lessons
            JOIN Schedules ON Schedules.id = Lessons.schedule_id
            WHERE Lessons.status = 'held'
        """)

        for lesson in lessons:
            start_dt = datetime.combine(lesson["lesson_date"], lesson["start_time"])
            deadline = start_dt + timedelta(minutes=5)

            if datetime.now() < deadline:
                await notify_deadline_passed(lesson["id"], deadline)
