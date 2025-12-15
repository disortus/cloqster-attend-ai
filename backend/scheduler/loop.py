import asyncio
from scheduler.attendance_service import attendance_tick

async def scheduler_loop():
    while True:
        await attendance_tick()
        await asyncio.sleep(60)