from schemas.users_sch import UserName, StdGroup
from schemas.students_sch import StudentUpdate, StudentDelete
from databases.postgres import database
from fastapi import HTTPException, File
from ws.redis_pubsub import publish_attend
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

                # вставляем новое
                await conn.execute("""
                    insert into Faces (student_id, img_path)
                    values ($1, $2)
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
            """SELECT Users.fullname, Groups.group_name FROM Students_Groups WHERE group_id = $1
            JOIN Users on Students_Groups.user_id = Users.id
            JOIN Groups on Students_Groups.group_id = Groups.id""", group["id"]
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

async def get_lessons():
    async with database.pool.acquire() as conn:
        rows = conn.fetch("SELECT * FROM Lessons")
        # if not rows:
        #    raise HTTPException(400, "занятия не найдены")
        return [dict(r) for r in rows] if rows else []

async def get_group_attends(curator_group_id: int):
    async with database.pool.acquire() as conn:

        attends = await conn.fetch("""
            SELECT A.id, A.student_id, A.status, A.come_at, A.mark_source,
                   S.group_id, U.fullname AS student_name
            FROM Attends A
            JOIN Lessons L ON A.lesson_id = L.id
            JOIN Schedules S ON L.schedule_id = S.id
            JOIN Users U ON A.student_id = U.id
            WHERE S.group_id = $1
        """, curator_group_id)

        return [dict(a) for a in attends]


async def curator_update_attend(curator_id: int, attend_id: int, new_status: str):
    async with database.pool.acquire() as conn:

        attend = await conn.fetchrow("""
            SELECT S.group_id, A.lesson_id
            FROM Attends A
            JOIN Lessons L ON A.lesson_id = L.id
            JOIN Schedules S ON L.schedule_id = S.id
            WHERE A.id = $1
        """, attend_id)

        if not attend:
            raise HTTPException(404, "Attend не найден")

        # куратор может менять только свою группу
        await conn.execute("""
            UPDATE Attends 
            SET status = $1, mark_source = 'teacher', marked_by = $2
            WHERE id = $3
        """, new_status, curator_id, attend_id)

        event = {
            "type": "attend_updated",
            "attend_id": attend_id,
            "lesson_id": attend["lesson_id"],
            "status": new_status,
            "source": "curator",
            "curator_id": curator_id
        }

        await publish_attend(
            event,
            channel=f"group_{attend['group_id']}"
        )




        return {"ok": True}
