from databases.postgres import database
from ws.websocket_manager import notify_group

LATE_MINUTES = 10
LEFT_TIMEOUT = 300  # 5 минут

async def attendance_tick():
    async with database.pool.acquire() as conn:
        rows = await conn.fetch("""
            select
                a.id,
                a.student_id,
                a.lesson_id,
                a.enter_at,
                a.last_seen,
                l.lesson_date as lesson_start,
                sg.group_id
            from Attends a
            join Lessons l on l.id = a.lesson_id
            join Students_Groups sg on sg.student_id = a.student_id
        """)

        for r in rows:
            await process_attend(conn, r)


async def process_attend(conn, r):
    now = conn.fetchval("select now()")

    # студент НИ РАЗУ не был замечен
    if r["last_seen"] is None:
        return

    # первый вход
    if r["enter_at"] is None:
        minutes = (r["last_seen"] - r["lesson_start"]).total_seconds() / 60
        status = "late" if minutes > LATE_MINUTES else "present"

        await conn.execute("""
            update Attends
            set come_at = last_seen,
                status = $1,
                marked_by = 'camera'
            where id = $2
        """, status, r["id"])

        await notify_group(r["group_id"], {
            "student_id": r["student_id"],
            "status": status
        })
        return

    # был, но давно не видели → НЕ absent, а просто ушёл
    if (now - r["last_seen"]).total_seconds() > LEFT_TIMEOUT:
        # статус НЕ меняем
        return