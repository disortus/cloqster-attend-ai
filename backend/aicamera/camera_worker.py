import cv2
import asyncio
from datetime import datetime
from aicamera.face_service import recognize_face
from databases.postgres import database

RTSP_URL = "rtsp://disortus:new_pass125@192.168.1.101:554/stream1"

async def camera_worker():
    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        print("❌ Камера не подключилась")
        return

    print("✅ Камера запущена")

    while True:
        ret, frame = cap.read()
        if not ret:
            await asyncio.sleep(1)
            continue

        student_id = recognize_face(frame)
        if student_id:
            await update_last_seen(student_id)

        await asyncio.sleep(0.2)


async def update_last_seen(student_id: int):
    async with database.pool.acquire() as conn:
        await conn.execute("""
            update Attends
            set last_seen = now()
            where student_id = $1
              and lesson_id = (
                  select id from Lessons
                  where group_id = (
                      select group_id from Students_Groups where student_id = $1
                  )
                  and now() between datetime and datetime + interval '2 hours'
                  limit 1
              )
        """, student_id)
