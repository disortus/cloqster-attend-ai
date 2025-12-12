from schemas.students_sch import Student
from databases.postgres import database
from fastapi import HTTPException, File
from pathlib import Path

file_path = Path(__file__).resolve().parent.parent / "databases" / "imgs"

async def add_face(data: Student, img: bytes = File(...)) -> dict:
    try:
        with open(f"{file_path}/{data.fullname}.jpg", "wb") as image:
            image.write(img)
            image.close()
        try:
            async with database.pool.acquire() as conn:
                std = await conn.fetchrow("SELECT id FROM Students WHERE fullname = $1", data.fullname)
                await conn.fetchrow("INSERT INTO Faces (student_id, img_path) VALUES ($1, $2)", std["id"], f"{file_path}/{data.fullname}.jpg")
                return {"ok": True}
        except Exception as e:
            print(f"error: {e}")
    except HTTPException as e:
        print(f"http error: {e}")

async def add_std(data: Student) -> dict:
    async with database.pool.acquire() as conn:
        try:
            await conn.fetchrow("INSERT INTO Students (fullname, course) VALUES ($1, $2)", data.fullname, data.course)
            return {"ok": True}
        except Exception as e:
            print(e)

async def get_std() -> list:
    async with database.pool.acquire() as conn:
        stds = await conn.fetch("SELECT * FROM Students")
        return [dict(std) for std in stds]
    
async def del_std(data: Student):
    async with database.pool.acquire() as conn:
        await conn.fetch("DELETE FROM Students WHERE fullname = $1", data.fullname)
        return {"ok": True}

async def ch_std(data: Student) -> dict:
    async with database.pool.acquire() as conn:
        try:
            await conn.fetchrow("UPDATE Students SET course = $1 WHERE fullname = $2", data.course, data.fullname)
            return {"ok": True}
        except Exception as e:
            print(e)

