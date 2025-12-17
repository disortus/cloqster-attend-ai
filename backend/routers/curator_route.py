from schemas.students_sch import StudentUpdate, StudentDelete
from schemas.users_sch import UserName
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

@cur_router.post("/add_face")
async def add_faces(student_id: int = Form(...), img: bytes = File(...)):
    from models.curators_models import add_face
    return await add_face(student_id, img)
@cur_router.get("/get_std")
async def get_stds(data: UserName):
    from models.curators_models import get_std
    return await get_std(data)

@cur_router.delete("/del_std")
async def del_stds(data: StudentDelete):
    from models.curators_models import del_std
    return await del_std(data)

@cur_router.put("/ch_std")
async def ch_stds(data: StudentUpdate):
    from models.curators_models import ch_std
    return await ch_std(data)

@cur_router.post("/camera/reload_faces")
async def reload_faces():
    from aicamera.face_db import load_faces
    await load_faces()
    return {"status": "ok"}