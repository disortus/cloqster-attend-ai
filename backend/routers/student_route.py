from fastapi import APIRouter, Depends
from auth.utils import require_role, get_current_user
from schemas.users_sch import UserName

std_router = admin_router = APIRouter(
    prefix="/student",
    tags=["Student"]
    # dependencies=[Depends(require_role("student"))]
)

@std_router.get("/schedule")
async def student_schedule(user = Depends(get_current_user)):
    from models.student_models import get_schedule_for_student
    return await get_schedule_for_student(user["id"])