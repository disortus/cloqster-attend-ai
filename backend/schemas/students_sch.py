from pydantic import BaseModel

class Student(BaseModel):
    fullname: str
    course: int

class StudentUpdate(BaseModel):
    fullname: str
    new_fullname: str

class StudentDelete(BaseModel):
    cur_fullname: str
    std_fullname: str

# class Face(Student):
#     img_path: str
