from schemas.users_sch import UserReg, UserOut, UserName, StdGroup, UserDelete
from schemas.groups_sch import Group, GroupDelete, GroupStdUpdate, CurGroupDelete
from schemas.students_sch import StudentUpdate
from auth.security import hash_password
from databases.postgres import database
from fastapi import HTTPException


# async def add_spec(data: Spec) -> dict:
#     async with database.pool.acquire() as conn:
#         try:
#             await conn.fetchrow(
#                 "INSERT INTO Lang (lang_name) VALUES ($1)", data.lang
#             )
#             await conn.fetchrow("INSERT INTO Qualify (qua_name) VALUES ($1)", data.qua_name)
#             q_id = await conn.fetchrow("SELECT id FROM Qualify WHERE qua_name = $1", data.qua_name)
#             await conn.fetchrow("INSERT INTO Spec (spec_name, qua_id) VALUES ($1, $2)", data.spec_name, q_id["id"])
#             return {"ok": True}
#         except Exception as e:
#             print(e)

async def get_specs() -> list:
    async with database.pool.acquire() as conn:
        specs = await conn.fetch(
            "SELECT Spec.spec_name, Qualify.qua_name FROM Spec "
            "JOIN Qualify ON Spec.qua_id = Qualify.id "
        )
        if not specs:
            raise HTTPException(400, "Специальности не найдены")
        return [dict(spec) for spec in specs]

async def add_group(data: Group) -> dict:
    async with database.pool.acquire() as conn:
        try:
            spec = await conn.fetchrow("SELECT id FROM Spec WHERE spec_name = $1", data.spec_name)
            if not spec:
                raise HTTPException(400, "Специальность не найдена")
            lang = await conn.fetchrow("SELECT id FROM Lang WHERE lang_name = $1", data.lang)
            if not lang:
                raise HTTPException(400, "Язык не найден")
            qua = await conn.fetchrow("SELECT id FROM Qualify WHERE qua_name = $1", data.qua_name)
            if not qua:
                raise HTTPException(400, "Квалификация не найдена")
            await conn.fetchrow(
                "INSERT INTO Groups (group_name, spec_id, lang_id, qua_id) VALUES ($1, $2, $3, $4)",
                data.group_name,
                spec["id"],
                lang["id"],
                qua["id"]
            )
            return {"ok": True}
        except Exception as e:
            print(e)
            raise HTTPException(400, "Группа с таким именем уже существует")

async def get_groups() -> list:
    async with database.pool.acquire() as conn:
        groups = await conn.fetch(
            "SELECT Groups.group_name, Spec.spec_name, Lang.lang_name, Qualify.qua_name FROM Groups "
            "JOIN Spec ON Groups.spec_id = Spec.id "
            "JOIN Lang ON Groups.lang_id = Lang.id "
            "JOIN Qualify ON Groups.qua_id = Qualify.id "
        )
        if not groups:
            raise HTTPException(400, "Группы не найдены")
        return [dict(group) for group in groups]

async def reg_user(data: UserReg) -> UserOut:
    async with database.pool.acquire() as conn:
        try:
            user = await conn.fetchrow("""
                INSERT INTO Users (email, password, fullname, role)
                VALUES ($1, $2, $3, $4)
                RETURNING email, fullname, role
            """,
            data.email,
            hash_password(data.password),
            data.fullname,
            data.role)
        except Exception as e:
            print(e)
            raise HTTPException(400, "Такой логин уже существует")

        return UserOut(**dict(user))
    
async def get_cur(name: UserName) -> list:
    async with database.pool.acquire() as conn:
        users = await conn.fetch(
            "SELECT fullname FROM Users WHERE fullname = $1 AND role = 'curator'",
            name.fullname
        )
        if not users:
            raise HTTPException(400, "Кураторы не найдены")
        return [UserName(**dict(r)) for r in users]

async def get_teach(name: UserName) -> list:
    async with database.pool.acquire() as conn:
        users = await conn.fetch(
            "SELECT fullname FROM Users WHERE fullname = $1 AND role = 'teacher'",
            name.fullname
        )
        if not users:
            raise HTTPException(400, "Преподаватели не найдены")
        return [UserName(**dict(r)) for r in users]

async def get_admin(name: UserName) -> list:
    async with database.pool.acquire() as conn:
        users = await conn.fetch(
            "SELECT fullname FROM Users WHERE fullname = $1 AND role = 'admin'",
            name.fullname
        )
        if not users:
            raise HTTPException(400, "Администраторы не найдены")
        return [UserName(**dict(r)) for r in users]

async def get_std(name: UserName) -> list:
    async with database.pool.acquire() as conn:
        users = await conn.fetch(
            "SELECT fullname FROM Users WHERE fullname = $1 AND role = 'student'",
            name.fullname
        )
        if not users:
            raise HTTPException(400, "Студенты не найдены")
        return [UserName(**dict(r)) for r in users]

async def add_std_to_group(data: StdGroup) -> dict:
    async with database.pool.acquire() as conn:
        try:
            group = await conn.fetchrow("SELECT id FROM Groups WHERE group_name = $1", data.group_name)
            std = await conn.fetchrow("SELECT id FROM Users WHERE fullname = $1 AND role = 'student'", data.fullname)
            await conn.fetchrow(
                "INSERT INTO Students_Groups (student_id, group_id) VALUES ($1, $2)",
                std["id"], group["id"]
            )
            return {"ok": True}
        except Exception as e:
            print(e)
            raise HTTPException(400, "Ошибка при добавлении студента в группу")

async def get_std_in_group() -> list:
    async with database.pool.acquire() as conn:
        students = await conn.fetch(
            "SELECT Users.fullname Groups.group_name FROM Students_Groups "
            "JOIN Users ON Students_Groups.student_id = Users.id "
            "JOIN Groups ON Students_Groups.group_id = Groups.id "
        )
        if not students:
            raise HTTPException(400, "Студенты в группах не найдены")
        return [UserName(**dict(s)) for s in students]

async def del_user(data: UserDelete) -> dict:
    async with database.pool.acquire() as conn:
        try:
            await conn.fetchrow(
                "DELETE FROM Users WHERE email = $1",
                data.email
            )
            return {"ok": True}
        except Exception as e:
            print(e)
            raise HTTPException(400, "Ошибка при удалении пользователя")

async def del_qroup(data: GroupDelete) -> dict:
    async with database.pool.acquire() as conn:
        try:
            await conn.fetchrow(
                "DELETE FROM Groups WHERE group_name = $1",
                data.group_name
            )
            return {"ok": True}
        except Exception as e:
            print(e)
            raise HTTPException(400, "Ошибка при удалении группы")

async def ch_std_group(data: GroupStdUpdate) -> dict:
    async with database.pool.acquire() as conn:
        try:
            group = await conn.fetchrow("SELECT id FROM Groups WHERE group_name = $1", data.group_name)
            if not group:
                raise HTTPException(400, "Группа не найдена")
            std = await conn.fetchrow("SELECT id FROM Users WHERE fullname = $1 AND role = 'student'", data.fullname)
            if not std:
                raise HTTPException(400, "Студент не найден")
            new_group = await conn.fetchrow("SELECT id FROM Groups WHERE group_name = $1", data.new_group_name)
            if not new_group:
                raise HTTPException(400, "Новая группа не найдена")
            await conn.fetchrow(
                "UPDATE Students_Groups SET group_id = $1 WHERE student_id = $2 AND group_id = $3",
                new_group["id"], std["id"], group["id"]
            )
            return {"ok": True}
        except Exception as e:
            print(e)
            raise HTTPException(400, "Ошибка при изменении группы студента")


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

async def ch_cur_group(data: GroupStdUpdate) -> dict:
    async with database.pool.acquire() as conn:
        try:
            group = await conn.fetchrow("SELECT id FROM Groups WHERE group_name = $1", data.group_name)
            if not group:
                raise HTTPException(400, "Группа не найдена")
            cur = await conn.fetchrow("SELECT id FROM Users WHERE fullname = $1 AND role = 'curator'", data.fullname)
            if not cur:
                raise HTTPException(400, "Куратор не найден")
            new_group = await conn.fetchrow("SELECT id FROM Groups WHERE group_name = $1", data.new_group_name)
            if not new_group:
                raise HTTPException(400, "Новая группа не найдена")
            await conn.fetchrow(
                "UPDATE Curators SET group_id = $1 WHERE user_id = $2 AND group_id = $3",
                new_group["id"], cur["id"], group["id"]
            )
            return {"ok": True}
        except Exception as e:
            print(e)
            raise HTTPException(400, "Ошибка при изменении группы куратора")

async def del_cur_group(data: CurGroupDelete) -> dict:
    async with database.pool.acquire() as conn:
        try:
            cur = await conn.fetchrow("SELECT id FROM Users WHERE fullname = $1 AND role = 'curator'", data.fullname)
            if not cur:
                raise HTTPException(400, "Куратор не найден")
            group = await conn.fetchrow("SELECT id FROM Groups WHERE group_name = $1", data.group_name)
            if not group:
                raise HTTPException(400, "Группа не найдена")
            await conn.fetchrow(
                "DELETE FROM Curators WHERE user_id = $1 AND group_id = $2",
                cur["id"], group["id"]
            )
            return {"ok": True}
        except Exception as e:
            print(e)
            raise HTTPException(400, "Ошибка при удалении куратора из группы")