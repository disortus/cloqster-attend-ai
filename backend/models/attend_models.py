from databases.postgres import database

async def get_absents_and_lates(lesson_id: int):
    async with database.pool.acquire() as conn:
        absents = await conn.fetch("""
            SELECT u.fullname
            FROM Attends a
            JOIN Users u ON u.id = a.student_id
            WHERE a.lesson_id = $1
              AND a.status = 'absent'
        """, lesson_id)

        lates = await conn.fetch("""
            SELECT u.fullname, a.come_at
            FROM Attends a
            JOIN Users u ON u.id = a.student_id
            WHERE a.lesson_id = $1
              AND a.status = 'late'
        """, lesson_id)

        curator = await conn.fetchrow("""
            SELECT Users.id AS curator_id
            FROM Lessons
            JOIN Schedules ON Schedules.id = Lessons.schedule_id
            JOIN Groups ON Groups.id = Schedules.group_id
            JOIN Users ON Users.id = Groups.curator_id
            WHERE Lessons.id = $1
        """, lesson_id)

    return absents, lates, curator["curator_id"]
