from fastapi import APIRouter, HTTPException
from databases.postgres import database
from ws.redis_pubsub import publish_attend

cam_router = APIRouter(prefix="/camera")


@cam_router.post("/mark")
async def accept_req(data: dict):

    async with database.pool.acquire() as conn:

        lesson = await conn.fetchrow(
            "SELECT id, group_id FROM Lessons WHERE schedule_id = $1",
            data["schedule_id"]
        )

        if not lesson:
            raise HTTPException(400, "lesson not found")

        await conn.execute("""
            INSERT INTO Attends (lesson_id, student_id, status, come_at, mark_source)
            VALUES ($1, $2, $3, $4, 'system')
        """, lesson["id"], data["id"], data["status"], data["time"])

        event = {
            "type": "attend_created",
            "lesson_id": lesson["id"],
            "group_id": lesson["group_id"],
            "student_id": data["id"],
            "status": data["status"],
            "source": "system"
        }

        await publish_attend(event)

        return {"ok": True}