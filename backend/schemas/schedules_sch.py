from pydantic import BaseModel
from enum import Enum
from datetime import time, date

class Weekday(int, Enum):
    monday = 1
    tuesday = 2
    wednesday = 3
    thursday = 4
    friday = 5

class LessonStatus(str, Enum):
    held = "held"
    canceled = "canceled"

class AttendStatus(str, Enum):
    absent = "absent"
    present = "present"
    late = "late"
    left = "left"

class MarkSource(str, Enum):
    system = "system"
    teacher = "teacher"

class Schedule(BaseModel):
    group_name: str
    weekday: Weekday
    start_time: time
    end_time: time
    subj_name: str
    teacher_fullname: str
    aud_number: str
    valid_from: date
    valid_to: date

class Lesson(BaseModel):
    group_name: str
    lesson_date: date
    status: LessonStatus