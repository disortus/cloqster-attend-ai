from fastapi import APIRouter, Depends
from auth.utils import require_role, get_current_user

teach_router = APIRouter(
    prefix="/teacher",
    tags=["teacher"]
    # dependencies=[Depends(require_role("teacher"))]
)

@teach_router.get("/attends")
async def teacher_attends(user=Depends(get_current_user)):
    from models.teacher_models import get_attends_for_group
    return await get_attends_for_group(user["id"])

@teach_router.put("/attend/{lesson_id}/{student_id}")
async def update_attend(lesson_id: int, student_id: int, status: str, user=Depends(get_current_user)):
    from models.teacher_models import update_attend_status
    return await update_attend_status(
        lesson_id=lesson_id,
        student_id=student_id,
        status=status,
        teacher_id=user["id"]
    )

@teach_router.get("/get_lessons")
async def get_less():
    from models.teacher_models import get_lessons
    return await get_lessons()