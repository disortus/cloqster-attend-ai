from schemas.students_sch import Student
from models.curators_models import add_face, add_std, ch_std, del_std, get_std
from fastapi import APIRouter, File, Form, Depends
from auth.utils import require_role
import json


cur_router = APIRouter(
    prefix="/curator",
    tags=["Curator"],
    dependencies=[Depends(require_role("curator"))]
)

@cur_router.get("")
async def curator_zone(user=Depends(require_role("curator"))):
    return {"msg": "welcome curator/teacher", "user": user}

@cur_router.post("/add_std")
async def add_stds(data: Student):
    return await add_std(data)

@cur_router.post("/add_face")
async def add_faces(data: str = Form(...), img: bytes = File(...)):
    data = Student(**json.loads(data))
    return await add_face(data, img)

@cur_router.get("/get_std")
async def get_stds():
    return await get_std()

@cur_router.delete("/del_std")
async def del_stds(data: Student):
    return await del_std(data)

@cur_router.put("/ch_std")
async def ch_stds(data: Student):
    return await ch_std(data)
