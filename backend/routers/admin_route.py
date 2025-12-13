from schemas.groups_sch import Group, GroupDelete
from schemas.users_sch import UserReg, UserOut, UserName, StdGroup, UserDelete
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
async def fetch_specs():
    from models.admin_models import get_specs
    return await get_specs()

# @admin_router.post("/specs")
# async def create_spec(data: Spec):
#     from models.admin_models import add_spec
#     return await add_spec(data)

@admin_router.post("/groups", response_model=dict)
async def create_group(data: Group):
    from models.admin_models import add_group
    return await add_group(data)

@admin_router.get("/groups", response_model=list)
async def fetch_groups():
    from models.admin_models import get_groups
    return await get_groups()

@admin_router.post("/register", response_model=UserOut)
async def register_user(data: UserReg):
    from models.admin_models import reg_user
    return await reg_user(data)

@admin_router.post("/get_curator", response_model=list)
async def get_curator(fullname: UserName):
    from models.admin_models import get_cur
    return await get_cur(fullname)

@admin_router.post("/get_teacher", response_model=list)
async def get_teacher(fullname: UserName):
    from models.admin_models import get_teach
    return await get_teach(fullname)

@admin_router.post("/get_student", response_model=list)
async def get_student(fullname: UserName):
    from models.admin_models import get_std
    return await get_std(fullname)

@admin_router.post("/get_admin", response_model=list)
async def get_admins(fullname: UserName):
    from models.admin_models import get_admin
    return await get_admin(fullname)

@admin_router.post("/add_std_to_group", response_model=dict)
async def add_std_to_groups(data: StdGroup):
    from models.admin_models import add_std_to_group
    return await add_std_to_group(data)

@admin_router.get("/std_in_groups", response_model=list)
async def get_std_in_groups():
    from models.admin_models import get_std_in_group
    return await get_std_in_group()

@admin_router.delete("/delete_group", response_model=dict)
async def delete_group(data: GroupDelete):
    from models.admin_models import del_qroup
    return await del_qroup(data)

@admin_router.delete("/delete_user", response_model=dict)
async def delete_user(data: UserDelete):
    from models.admin_models import del_user
    return await del_user(data)
