from schemas.users_sch import UserName
from schemas.students_sch import StudentUpdate, StudentDelete
from databases.postgres import database
from fastapi import HTTPException, File
from pathlib import Path

file_path = Path(__file__).resolve().parent.parent / "databases" / "imgs"

async def add_face(data: UserName, img: bytes = File(...)) -> dict:
    try:
        with open(f"{file_path}/{data.fullname}.jpg", "wb") as image:
            image.write(img)
            image.close()

            async with database.pool.acquire() as conn:
                std = await conn.fetchrow("SELECT id FROM Users WHERE fullname = $1 AND role = 'student'", data.fullname)
                if not std:
                    raise HTTPException(400, "Студент не найден")
                await conn.fetchrow("INSERT INTO Faces (student_id, img_path) VALUES ($1, $2)", std["id"], f"{file_path}/{data.fullname}.jpg")
                return {"ok": True}
    except Exception as e:
        print(f"error: {e}")
        raise HTTPException(400, "Ошибка при добавлении лица студента")

async def get_std(data: UserName) -> list:
    async with database.pool.acquire() as conn:
        cur = await conn.fetchrow("SELECT id FROM Users WHERE fullname = $1 AND role = 'curator'", data.fullname)
        if not cur:
            raise HTTPException(400, "Куратор не найден")
        group = await conn.fetchrow("SELECT id FROM Groups WHERE curator_id = $1", cur["id"])
        if not group:
            raise HTTPException(400, "Куратор не назначен ни в одну группу")
        stds = await conn.fetch(
            "SELECT Users.fullname, Groups.group_name FROM Students_Groups WHERE group_id = $1", group["id"]
        )
        return [dict(std) for std in stds]
    
async def del_std(data: StudentDelete) -> dict:
    async with database.pool.acquire() as conn:
        cur = await conn.fetchrow("SELECT id FROM Users WHERE fullname = $1 AND role = 'curator'", data.cur_fullname)
        if not cur:
            raise HTTPException(400, "Куратор не найден")
        group = await conn.fetchrow("SELECT id FROM Groups WHERE curator_id = $1", cur["id"])
        if not group:
            raise HTTPException(400, "Куратор не назначен ни в одну группу")
        std = await conn.fetchrow("SELECT id FROM Users WHERE fullname = $1 AND role = 'student'", data.std_fullname)
        if not std:
            raise HTTPException(400, "Студент не найден")
        try:
            await conn.fetchrow(
                "DELETE FROM Students_Groups WHERE student_id = $1 AND group_id = $2",
                std["id"], group["group_id"]
            )
        except Exception as e:
            print(e)
            raise HTTPException(400, "Ошибка при удалении студента из группы")
        return {"ok": True}

async def ch_std(data: StudentUpdate) -> dict:
    async with database.pool.acquire() as conn:
        try:
            await conn.fetchrow(
                "UPDATE Users SET fullname = $1 WHERE fullname = $2 AND role = 'student'",
                data.new_fullname, data.fullname
            )
            return {"ok": True}
        except Exception as e:
            print(e)
            raise HTTPException(400, "Ошибка при изменении данных студента")

