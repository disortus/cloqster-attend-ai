from schemas.users_sch import UserName, StdGroup
from schemas.students_sch import StudentUpdate, StudentDelete
from databases.postgres import database
from fastapi import HTTPException, File
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent.parent / "databases" / "imgs"
BASE_PATH.mkdir(parents=True, exist_ok=True)

async def add_face(student_id: int, img: bytes = File(...)) -> dict:
    async with database.pool.acquire() as conn:
        async with conn.transaction():
            student = await conn.fetchrow("""
                select id
                from Users
                where id = $1 and role = 'student'
            """, student_id)
            if not student:
                raise HTTPException(400, "Студент не найден")

            # имя файла = student_id
            img_path = BASE_PATH / f"{student_id}.jpg"
            try:
                # сохраняем файл
                with open(img_path, "wb") as f:
                    f.write(img)

                # деактивируем старое лицо (если было)
                await conn.execute("""
                    update Faces
                    set is_active = false
                    where student_id = $1
                """, student_id)

                # вставляем новое
                await conn.execute("""
                    insert into Faces (student_id, img_path, is_active)
                    values ($1, $2, true)
                """, student_id, str(img_path))
            except Exception as e:
                print(e)
                raise HTTPException(500, "Ошибка при сохранении лица")
    return {"ok": True}

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

