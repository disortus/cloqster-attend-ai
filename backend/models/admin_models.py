from auth.security import hash_password
from schemas.users_sch import UserReg, UserOut, UserName, StdGroup, UserDelete
from schemas.groups_sch import Spec, Group
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
        return [dict(spec) for spec in specs]

async def add_group(data: Group) -> dict:
    async with database.pool.acquire() as conn:
        try:
            spec = await conn.fetchrow("SELECT id FROM Spec WHERE spec_name = $1", data.spec_name)
            lang = await conn.fetchrow("SELECT id FROM Lang WHERE lang_name = $1", data.lang)
            qua = await conn.fetchrow("SELECT id FROM Qualify WHERE qua_name = $1", data.qua_name)
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
        return [UserName(**dict(r)) for r in users]

async def get_teach(name: UserName) -> list:
    async with database.pool.acquire() as conn:
        users = await conn.fetch(
            "SELECT fullname FROM Users WHERE fullname = $1 AND role = 'teacher'",
            name.fullname
        )
        return [UserName(**dict(r)) for r in users]

async def get_admin(name: UserName) -> list:
    async with database.pool.acquire() as conn:
        users = await conn.fetch(
            "SELECT fullname FROM Users WHERE fullname = $1 AND role = 'admin'",
            name.fullname
        )
        return [UserName(**dict(r)) for r in users]

async def get_std(name: UserName) -> list:
    async with database.pool.acquire() as conn:
        users = await conn.fetch(
            "SELECT fullname FROM Users WHERE fullname = $1 AND role = 'student'",
            name.fullname
        )
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

async def del_qroup(data: Group) -> dict:
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



