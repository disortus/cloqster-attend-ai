from databases.postgres import database
from fastapi import HTTPException
from schemas.users_sch import UserName

async def get_schedule(data: UserName) -> dict:
    async with database.pool.acquire() as conn:
        student_id = await conn.fetchrow("SELECT id FROM Users WHERE fullname = $1 AND role = 'student'", data.fullname)
        if not student_id:
            raise HTTPException(400, "студент не найден")
        group_id = await conn.fetchrow("SELECT group_id FROM Students_Groups WHERE student_id = $1", student_id)
        if not group_id:
            raise HTTPException(400, "группа не найдена")
        schedule = await conn.fetch("""SELECT Groups.group_name, Schedules.weekday, Schedules.start_time, Schedules.end_time, 
            Subjects.subj_name, Users.fullname AS teacher_fullname, Audience.aud_number, 
            Schedules.valid_from, Schedules.valid_to 
            FROM Schedules
            WHERE group_id = $1
            JOIN Groups ON Schedules.group_id = Groups.id
            JOIN Users ON Schedules.teacher_id = Users.id
            JOIN Subjects ON Schedules.subj_id = Subjects.id 
            JOIN Audience ON Schedules.aud_id = Audience.id""", group_id)
        if not schedule:
            raise HTTPException(400, "Расписания не найдены")
        return [dict(sch) for sch in schedule]
    
