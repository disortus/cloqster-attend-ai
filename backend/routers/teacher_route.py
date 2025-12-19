from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from auth.utils import require_role, get_current_user
from ws.attends_ws import broadcast

teach_router = APIRouter(
    prefix="/teacher",
    tags=["teacher"]
    # dependencies=[Depends(require_role("teacher"))]
)

@teach_router.get("/attends/{lesson_id}")
async def teacher_get_attends(
    lesson_id: int,
    user=Depends(require_role("teacher"))
):
    from models.teacher_models import get_attends_for_lesson
    teacher_id = user["id"]
    return await get_attends_for_lesson(teacher_id, lesson_id)


@teach_router.put("/attends/{attend_id}")
async def teacher_edit_attend(
    attend_id: int,
    new_status: str,
    user=Depends(require_role("teacher"))
):
    from models.teacher_models import teacher_update_attend
    teacher_id = user["id"]
    return await teacher_update_attend(teacher_id, attend_id, new_status)

@teach_router.get("/get_lessons")
async def get_less():
    from models.teacher_models import get_lessons
    return await get_lessons()