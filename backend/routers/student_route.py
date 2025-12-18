from fastapi import APIRouter, Depends
from auth.utils import require_role
from schemas.users_sch import UserName

std_router = admin_router = APIRouter(
    prefix="/student",
    tags=["Student"]
    # dependencies=[Depends(require_role("student"))]
)

@std_router.post("/get_schedule", response_model=dict)
async def get_sch(data: UserName) -> dict:
    from models.student_models import get_schedule
    return await get_schedule(data)