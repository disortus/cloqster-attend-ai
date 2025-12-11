from schemas.groups_sch import Spec, Group
from fastapi import APIRouter, Depends

admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.get("/specs")
async def fetch_specs():
    from models.admin_models import get_specs
    return await get_specs()

@admin_router.post("/specs")
async def create_spec(data: Spec):
    from models.admin_models import add_spec
    return await add_spec(data)

@admin_router.post("/groups")
async def create_group(data: Group):
    from models.admin_models import add_group
    return await add_group(data)

@admin_router.get("/groups")
async def fetch_groups():
    from models.admin_models import get_groups
    return await get_groups()

@admin_router.post("/register")
async def register_user(data: 'UserReg'):
    from models.admin_models import reg_user
    return await reg_user(data)