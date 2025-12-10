from schemas.students_sch import Student
from models.curators_models import add_face, add_std
from fastapi import APIRouter, File, Form
import json


cur_router = APIRouter(prefix="/cur")



@cur_router.post("add_std")
async def add_stds(data: Student):
    return await add_std(data)

@cur_router.post("add_face")
async def add_faces(data: str = Form(...), img: bytes = File(...)):
    print(data)
    data = Student(**json.loads(data))
    return await add_face(data, img)