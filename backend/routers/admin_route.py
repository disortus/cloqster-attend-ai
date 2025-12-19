from schemas.groups_sch import Group, GroupDelete, GroupStdUpdate, GroupCurUpdate
from schemas.users_sch import UserReg, UserOut, UserName, StdGroup, UserDelete
from schemas.subj_sch import Subject
from schemas.aud_sch import AudSchema
from schemas.schedules_sch import Schedule
from schemas.students_sch import StudentUpdate
from fastapi import APIRouter, Depends
from auth.utils import require_role

admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
    # dependencies=[Depends(require_role("admin"))]
)

@admin_router.get("")
async def admin_panel(user=Depends(require_role("admin"))):
    return {"msg": "admin access", "user": user}

@admin_router.get("/specs")
async def fetch_specs() -> list:
    from models.admin_models import get_specs
    return await get_specs()

@admin_router.post("/groups", response_model=dict)
async def create_group(data: Group) -> dict:
    from models.admin_models import add_group
    return await add_group(data)

@admin_router.get("/groups", response_model=list)
async def fetch_groups() -> list:
    from models.admin_models import get_groups
    return await get_groups()

@admin_router.post("/register", response_model=UserOut)
async def register_user(data: UserReg) -> UserOut:
    from models.admin_models import reg_user
    return await reg_user(data)

@admin_router.get("/get_curator", response_model=list)
async def get_curator() -> list:
    from models.admin_models import get_cur
    return await get_cur()

@admin_router.get("/get_teacher", response_model=list)
async def get_teacher() -> list:
    from models.admin_models import get_teach
    return await get_teach()

@admin_router.get("/get_student", response_model=list)
async def get_student() -> list:
    from models.admin_models import get_std
    return await get_std()

@admin_router.get("/get_admin", response_model=list)
async def get_admins() -> list:
    from models.admin_models import get_admin
    return await get_admin()

@admin_router.get("/get_users", response_model=list)
async def get_us() -> list:
    from models.admin_models import get_users
    return await get_users() 

@admin_router.post("/add_std_to_group", response_model=dict)
async def add_std_to_groups(data: StdGroup) -> dict:
    from models.admin_models import add_std_to_group
    return await add_std_to_group(data)

@admin_router.get("/std_in_groups", response_model=list)
async def get_std_in_groups() -> list:
    from models.admin_models import get_std_in_group
    return await get_std_in_group()

@admin_router.delete("/delete_group", response_model=dict)
async def delete_group(data: GroupDelete) -> dict:
    from models.admin_models import del_qroup
    return await del_qroup(data)

@admin_router.delete("/delete_user", response_model=dict)
async def delete_user(data: UserDelete) -> dict:
    from models.admin_models import del_user
    return await del_user(data)

@admin_router.put("/change_student", response_model=dict)
async def change_student(data: StudentUpdate) -> dict:
    from models.admin_models import ch_std
    return await ch_std(data)

@admin_router.put("/change_curator_group", response_model=dict)
async def change_curator_group(data: GroupCurUpdate) -> dict:
    from models.admin_models import ch_cur_group
    return await ch_cur_group(data)

@admin_router.delete("/remove_student_from_group", response_model=dict)
async def remove_student_from_group(data: StdGroup) -> dict:
    from models.admin_models import del_std_from_group
    return await del_std_from_group(data)

@admin_router.post("/add_subject", response_model=dict)
async def add_subject(data: Subject) -> dict:
    from models.admin_models import add_subject
    return await add_subject(data)

@admin_router.post("/add_schedule", response_model=dict)
async def add_schedule(data: Schedule) -> dict:
    from models.admin_models import add_schedule
    return await add_schedule(data)

@admin_router.get("/schedules", response_model=list)
async def fetch_schedules() -> list:
    from models.admin_models import get_schedules
    return await get_schedules()

@admin_router.get("/subjects", response_model=list)
async def fetch_subjects() -> list:
    from models.admin_models import get_subjects
    return await get_subjects()

@admin_router.delete("/delete_subject", response_model=dict)
async def delete_subject(data: Subject) -> dict:
    from models.admin_models import del_subject
    return await del_subject(data)

@admin_router.delete("/delete_schedule", response_model=dict)
async def delete_schedule(data: GroupDelete) -> dict:
    from models.admin_models import del_schedule
    return await del_schedule(data)

@admin_router.post("/add_audience", response_model=dict)
async def add_audience(data: AudSchema) -> dict:
    from models.admin_models import add_aud
    return await add_aud(data)

@admin_router.get("/audiences", response_model=list)
async def fetch_audiences() -> list:
    from models.admin_models import get_aud
    return await get_aud()

@admin_router.delete("/delete_audience", response_model=dict)
async def delete_audience(data: AudSchema) -> dict:
    from models.admin_models import del_aud
    return await del_aud(data)

@admin_router.get("/get_attends", response_model=list)
async def fetch_attends() -> list:
    from models.admin_models import get_attends
    return await get_attends()

@admin_router.get("/dashboard_stats", response_model=dict)
async def dashboard_stats() -> dict:
    from models.admin_models import dashboard_metrics
    return await dashboard_metrics()

@admin_router.get("/attendance_report", response_model=list)
async def attendance_report() -> list:
    from models.admin_models import dashboard_trend
    return await dashboard_trend()

@admin_router.get("/performance_report", response_model=dict)
async def performance_report() -> dict:
    from models.admin_models import dashboard_today_breakdown
    return await dashboard_today_breakdown()

@admin_router.get("/dashbord_overview", response_model=dict)
async def dashboard_overview() -> dict:
    from models.admin_models import dashboard_activity
    return await dashboard_activity()

@admin_router.get("/attends")
async def admin_get_all(
    user=Depends(require_role("admin"))
):
    from models.admin_models import admin_get_attends
    return await admin_get_attends()


@admin_router.put("/attends/{attend_id}")
async def admin_edit_attend(
    attend_id: int,
    new_status: str,
    user=Depends(require_role("admin"))
):
    from models.admin_models import admin_update_attend
    admin_id = user["id"]
    return await admin_update_attend(admin_id, attend_id, new_status)