from fastapi import APIRouter, Depends
from datetime import datetime
from models.aicamera_models import update_attendance_from_camera
from schemas.camera_sch import CameraDetection
from ws.manager import manager
from databases.postgres import database

aicamera_router = APIRouter(prefix="/api/aicamera", tags=["AICamera"])

@aicamera_router.post("/update")
async def camera_update(data: CameraDetection):
    result = await update_attendance_from_camera(
        aud_id=data.aud_id,
        student_id=data.student_id,
        timestamp=datetime.fromisoformat(data.timestamp)
    )

    if result.get("status") == "no_active_lesson":
        return {"status": "ignored"}

    # Формируем сообщение для фронта
    message = {
        "type": "attendance_update",
        "data": {
            "lesson_id": result["lesson_id"],
            "group_id": result["group_id"],
            "student_id": result["student_id"],
            "student_name": result["student_name"],
            "action": result["action"],  # "present" или "seen"
            "timestamp": result["timestamp"]
        }
    }

    # Отправляем нужным людям
    async with database.pool.acquire() as conn:
        # Админы — получают всё
        await manager.broadcast_to_admins(message)

        # Куратор группы
        group = await conn.fetchrow("SELECT curator_id FROM Groups WHERE id = $1", result["group_id"])
        if group and group["curator_id"]:
            await manager.broadcast_to_curator(group["curator_id"], message)

        # Учителя — получают все текущие обновления (упрощённо)
        await manager.broadcast_to_teachers(message)

    return {"status": "updated"}