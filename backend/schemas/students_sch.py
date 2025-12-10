from pydantic import BaseModel

class Student(BaseModel):
    fullname: str
    course: int

# class Face(Student):
#     img_path: str
