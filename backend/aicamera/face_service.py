from deepface import DeepFace
from aicamera.face_db import FACE_DB

THRESHOLD = 0.6

def recognize_face(frame):
    for student_id, img_path in FACE_DB.items():
        try:
            res = DeepFace.verify(
                frame,
                img_path,
                enforce_detection=False,
                model_name="Facenet"
            )
            if res["verified"] and res["distance"] < THRESHOLD:
                return student_id
        except Exception:
            continue
    return None
