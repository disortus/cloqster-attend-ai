from datetime import date, datetime
from databases.postgres import database

async def create_today_lessons():
    today = date.today()
    weekday = today.isoweekday()

    if weekday > 5:
        return

    async with database.pool.acquire() as conn:
        schedules = await conn.fetch("""
            SELECT id
            FROM Schedules
            WHERE weekday = $1
              AND valid_from <= $2
              AND (valid_to is null or valid_to >= $2)
        """, weekday, today)

        for sch in schedules:
            await conn.execute("""
                INSERT INTO Lessons (schedule_id, lesson_date)
                VALUES ($1, $2)
                ON CONFLICT DO NOTHING
            """, sch["id"], today)

async def watch_lessons():
    now = datetime.now().time()

    async with database.pool.acquire() as conn:
        lessons = await conn.fetch("""
            SELECT Lessons.id, Schedules.group_id
            FROM Lessons
            JOIN Schedules on Schedules.id = Lessons.schedule_id
            WHERE Lessons.lesson_date = current_date
              AND Lessons.status = 'planned'
              AND Schedules.start_time <= $1
        """, now)

        for lesson in lessons:
            await conn.execute("""
                UPDATE Lessons
                SET status = 'held'
                WHERE id = $1
            """, lesson["id"])

            await init_attends(lesson["id"], lesson["group_id"])

async def init_attends(lesson_id: int, group_id: int):
    async with database.pool.acquire() as conn:
        students = await conn.fetch("""
            SELECT student_id
            FROM Students_Groups
            WHERE group_id = $1
        """, group_id)

        for s in students:
            await conn.execute("""
                INSERT INTO Attends (
                    lesson_id,
                    student_id,
                    status,
                    mark_source
                )
                VALUES ($1, $2, 'absent', 'system')
                ON CONFLICT DO NOTHING
            """, lesson_id, s["student_id"])