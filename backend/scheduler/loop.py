import asyncio
from scheduler.lessons import create_today_lessons, watch_lessons

async def scheduler_loop():
    while True:
        await create_today_lessons()
        await watch_lessons()
        await asyncio.sleep(60)