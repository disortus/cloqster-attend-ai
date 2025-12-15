from schemas.users_sch import UserReg, UserOut, UserName, StdGroup, UserDelete
from schemas.groups_sch import Group, GroupDelete, GroupCurUpdate
from schemas.schedules_sch import Schedule
from schemas.subj_sch import Subject
from schemas.aud_sch import AudSchema
from schemas.students_sch import StudentUpdate
from auth.security import hash_password
from databases.postgres import database
from fastapi import HTTPException

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
            cur = await conn.fetchrow("SELECT id FROM Users WHERE fullname = $1 AND role = 'curator'", data.fullname)
            if not cur:
                raise HTTPException(400, "Куратор не найден")
            await conn.fetchrow(
                "INSERT INTO Groups (group_name, spec_id, lang_id, qua_id, curator_id) VALUES ($1, $2, $3, $4, $5)",
                data.group_name,
                spec["id"],
                lang["id"],
                qua["id"],
                cur["id"]
            )
            return {"ok": True}
        except Exception as e:
            print(e)
            raise HTTPException(400, "Группа с таким именем уже существует")

async def get_groups() -> list:
    async with database.pool.acquire() as conn:
        groups = await conn.fetch(
            "SELECT Groups.group_name, Spec.spec_name, Lang.lang_name, Qualify.qua_name, Users.fullname FROM Groups "
            "JOIN Spec ON Groups.spec_id = Spec.id "
            "JOIN Lang ON Groups.lang_id = Lang.id "
            "JOIN Qualify ON Groups.qua_id = Qualify.id "
            "JOIN Users ON Groups.curator_id = Users.id "
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
    
async def get_cur() -> list:
    async with database.pool.acquire() as conn:
        users = await conn.fetch(
            "SELECT fullname FROM Users WHERE role = 'curator'"
        )
        if not users:
            raise HTTPException(400, "Кураторы не найдены")
        return [UserName(**dict(r)) for r in users]

async def get_teach() -> list:
    async with database.pool.acquire() as conn:
        users = await conn.fetch(
            "SELECT fullname FROM Users WHERE role = 'teacher'"
        )
        if not users:
            raise HTTPException(400, "Преподаватели не найдены")
        return [UserName(**dict(r)) for r in users]

async def get_admin() -> list:
    async with database.pool.acquire() as conn:
        users = await conn.fetch(
            "SELECT fullname FROM Users WHERE role = 'admin'"
        )
        if not users:
            raise HTTPException(400, "Администраторы не найдены")
        return [UserName(**dict(r)) for r in users]

async def get_std() -> list:
    async with database.pool.acquire() as conn:
        users = await conn.fetch(
            "SELECT fullname FROM Users WHERE role = 'student'"
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

async def del_std_from_group(data: StdGroup) -> dict:
    async with database.pool.acquire() as conn:
        try:
            group = await conn.fetchrow("SELECT id FROM Groups WHERE group_name = $1", data.group_name)
            if not group:
                raise HTTPException(400, "Группа не найдена")
            std = await conn.fetchrow("SELECT id FROM Users WHERE fullname = $1 AND role = 'student'", data.fullname)
            if not std:
                raise HTTPException(400, "Студент не найден")
            await conn.fetchrow(
                "DELETE FROM Students_Groups WHERE student_id = $1 AND group_id = $2",
                std["id"], group["id"]
            )
            return {"ok": True}
        except Exception as e:
            print(e)
            raise HTTPException(400, "Ошибка при удалении студента из группы")


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

async def ch_cur_group(data: GroupCurUpdate) -> dict:
    async with database.pool.acquire() as conn:
        try:
            cur = await conn.fetchrow("SELECT id FROM Users WHERE fullname = $1 AND role = 'curator'", data.fullname)
            if not cur:
                raise HTTPException(400, "Куратор не найден")
            await conn.fetchrow(
                "UPDATE Groups SET curator_id = $1 WHERE group_name = $2",
                cur["id"], data.group_name
            )
            return {"ok": True}
        except Exception as e:
            print(e)
            raise HTTPException(400, "Ошибка при изменении куратора группы")

async def add_schedule(data: Schedule) -> dict:
    async with database.pool.acquire() as conn:
        try:
            group = await conn.fetchrow("SELECT id FROM Groups WHERE group_name = $1", data.group_name)
            if not group:
                raise HTTPException(400, "Группа не найдена")
            teacher = await conn.fetchrow("SELECT id FROM Users WHERE fullname = $1 AND role = 'teacher'", data.teacher_fullname)
            if not teacher:
                raise HTTPException(400, "Преподаватель не найден")
            subj = await conn.fetchrow("SELECT id FROM Subjects WHERE subj_name = $1", data.subj_name)
            if not subj:
                raise HTTPException(400, "Предмет не найден")
            aud = await conn.fetchrow("SELECT id FROM Audience WHERE aud_number = $1", data.aud_number)
            if not aud:
                raise HTTPException(400, "Аудитория не найдена")
            await conn.fetchrow(
                "INSERT INTO Schedules (group_id, weekday, start_time, end_time, teacher_id, subj_id, aud_id, valid_from, valid_to)"
                "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
                group["id"], data.weekday, data.start_time, data.end_time,
                teacher["id"], subj["id"], aud["id"], data.valid_from, data.valid_to
            )
            return {"ok": True}
        except Exception as e:
            print(e)
            raise HTTPException(400, "Ошибка при добавлении расписания")

async def get_schedules() -> list:
    async with database.pool.acquire() as conn:
        schedules = await conn.fetch(
            "SELECT Groups.group_name, Schedules.weekday, Schedules.start_time, Schedules.end_time, "
            "Subjects.subj_name, Users.fullname AS teacher_fullname, Audience.aud_number, "
            "Schedules.valid_from, Schedules.valid_to "
            "FROM Schedules "
            "JOIN Groups ON Schedules.group_id = Groups.id "
            "JOIN Users ON Schedules.teacher_id = Users.id "
            "JOIN Subjects ON Schedules.subj_id = Subjects.id "
            "JOIN Audience ON Schedules.aud_id = Audience.id "
        )
        if not schedules:
            raise HTTPException(400, "Расписания не найдены")
        return [dict(sch) for sch in schedules]

async def add_subject(data: Subject) -> dict:
    async with database.pool.acquire() as conn:
        try:
            spec = await conn.fetchrow("SELECT id FROM Spec WHERE spec_name = $1", data.spec_name)
            if not spec:
                raise HTTPException(400, "Специальность не найдена")
            await conn.fetchrow(
                "INSERT INTO Subjects (subj_name, spec_id) VALUES ($1, $2)",
                data.subj_name, spec["id"]
            )
            return {"ok": True}
        except Exception as e:
            print(e)
            raise HTTPException(400, "Ошибка при добавлении предмета")

async def get_subjects() -> list:
    async with database.pool.acquire() as conn:
        subjects = await conn.fetch(
            "SELECT Subjects.subj_name, Spec.spec_name FROM Subjects "
            "JOIN Spec ON Subjects.spec_id = Spec.id "
        )
        if not subjects:
            raise HTTPException(400, "Предметы не найдены")
        return [dict(subj) for subj in subjects]

async def del_subject(data: Subject) -> dict:
    async with database.pool.acquire() as conn:
        try:
            await conn.fetchrow(
                "DELETE FROM Subjects WHERE subject_name = $1",
                data.subj_name
            )
            return {"ok": True}
        except Exception as e:
            print(e)
            raise HTTPException(400, "Ошибка при удалении предмета")

async def del_schedule(data: GroupDelete) -> dict:
    async with database.pool.acquire() as conn:
        try:
            await conn.fetchrow(
                "DELETE FROM Schedules WHERE group_id = (SELECT id FROM Groups WHERE group_name = $1)",
                data.group_name
            )
            return {"ok": True}
        except Exception as e:
            print(e)
            raise HTTPException(400, "Ошибка при удалении расписания")

async def add_aud(data: AudSchema) -> dict:
    async with database.pool.acquire() as conn:
        try:
            aud_type_id = await conn.fetchrow("SELECT id FROM Audience_types WHERE aud_type = $1", data.aud_type)
            await conn.fetchrow(
                "INSERT INTO Audience (aud_number, build, aud_type_id) VALUES ($1, $2, $3)", data.aud_number, data.build, aud_type_id["id"]
            )
            return {"ok": True}
        except Exception as e:
            print(e)
            raise HTTPException(400, "Ошибка при добавлении аудитории")

async def get_aud() -> list:
    async with database.pool.acquire() as conn:
        audience = await conn.fetch(
            "SELECT Audience.aud_number, Audience.build, Audience_types.aud_type FROM Audience "
            "JOIN Audience_types ON Audience.aud_type_id = Audience_types.id "
        )
        if not audience:
            raise HTTPException(400, "Аудитории не найдены")
        return [dict(aud) for aud in audience]

async def del_aud(data: AudSchema) -> dict:
    async with database.pool.acquire() as conn:
        try:
            await conn.fetchrow(
                "DELETE FROM Audience WHERE aud_number = $1",
                data.aud_number
            )
            return {"ok": True}
        except Exception as e:
            print(e)
            raise HTTPException(400, "Ошибка при удалении аудитории")

async def get_attends() -> list:
    async with database.pool.acquire() as conn:
        attends = await conn.fetch(
            "SELECT Attends.id, Users.fullname, Lessons.lesson_date, Attends.status, Attends.come_at, Attends.last_seen "
            "FROM Attends "
            "JOIN Users ON Attends.student_id = Users.id "
            "JOIN Lessons ON Attends.lesson_id = Lessons.id "
        )
        if not attends:
            raise HTTPException(400, "Посещаемость не найдена")
        return [dict(att) for att in attends]