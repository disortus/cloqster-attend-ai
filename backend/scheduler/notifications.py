from datetime import datetime
from redis.publisher import publish_event
from models.attend_models import get_absents_and_lates

async def notify_deadline_passed(lesson_id: int, run_at: datetime):
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    scheduler = AsyncIOScheduler()
    scheduler.start()

    scheduler.add_job(
        send_deadline_report,
        "date",
        run_date=run_at,
        args=[lesson_id]
    )

async def send_deadline_report(lesson_id: int):
    absents, lates, curator_id = await get_absents_and_lates(lesson_id)

    event = {
        "type": "deadline",
        "lesson_id": lesson_id,
        "absent": absents,
        "late": lates,
        "curator_id": curator_id
    }

    await publish_event("deadline", event)
