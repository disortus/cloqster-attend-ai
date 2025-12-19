import asyncio
from scheduler.lessons import create_today_lessons, watch_lessons
from scheduler.deadlines import schedule_deadlines

async def scheduler_loop():
    while True:
        await create_today_lessons()
        await watch_lessons()
        await schedule_deadlines()
        await asyncio.sleep(60)