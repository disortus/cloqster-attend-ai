import cv2
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import asyncio
import threading
from datetime import datetime, time
import aiohttp
import time as time_mod
from deepface import DeepFace
from postgres import database

BASE_DIR = Path(__file__).resolve().parent.parent
IMGS_PATH = BASE_DIR / "backend/databases/imgs"
FASTAPI_URL = "http://localhost:5000/camera/mark"
RTSP_URL = "rtsp://disortus:new_pass125@192.168.1.101:554/stream1"

RECOGNITION_INTERVAL = 1.0
DISTANCE_THRESHOLD = 1.0  # для ArcFace
STATE_TIMEOUT = 15

executor = ThreadPoolExecutor(max_workers=2)
frame_lock = threading.Lock()
cache_lock = threading.Lock()

latest_frame = None
last_recognition_time = 0
student_state = {}
last_seen = {}

schedule_cache = {}

COOLDOWN_PER_PERSON = 0  # для теста

# -------------------------- Расписание --------------------------

async def load_schedule():
    global schedule_cache
    async with database.pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, weekday, start_time, end_time FROM Schedules
            ORDER BY weekday, start_time
        """)
    new_cache = {}
    for row in rows:
        wd = row["weekday"]
        if wd not in new_cache:
            new_cache[wd] = []
        new_cache[wd].append((row["id"], row["start_time"], row["end_time"]))
    with cache_lock:
        schedule_cache = new_cache
    print(f"Расписание загружено: {len(rows)} записей")

def get_current_lesson(weekday: int, cur_time: time):
    with cache_lock:
        lessons = schedule_cache.get(weekday, [])
    for sched_id, start, end in lessons:
        if start <= cur_time <= end:
            return (sched_id, start, end)
    return None

# -------------------------- Статусы студентов --------------------------

def update_student_status(student_id: str, now: datetime, lesson: tuple | None):
    global student_state
    current_time = time_mod.time()
    state = student_state.get(student_id, {
        "current_status": "absent",
        "final_status": "absent",
        "last_seen": 0,
        "lesson_key": lesson,
        "first_seen_during_lesson": None
    })

    if state["lesson_key"] != lesson:
        state = {
            "current_status": "absent",
            "final_status": "absent",
            "last_seen": 0,
            "lesson_key": lesson,
            "first_seen_during_lesson": None
        }

    if lesson:
        start_time, end_time = lesson[1], lesson[2]
        if state["first_seen_during_lesson"] is None:
            state["first_seen_during_lesson"] = current_time
            if now.time() > start_time:
                state["final_status"] = "late"
            else:
                state["final_status"] = "present"
        state["current_status"] = "present"
        state["last_seen"] = current_time

    student_state[student_id] = state
    return state["current_status"], state["final_status"]

# -------------------------- Камера --------------------------

async def capture_frames(cap: cv2.VideoCapture):
    global latest_frame
    def read_loop():
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                time_mod.sleep(0.1)
                continue
            with frame_lock:
                latest_frame = frame.copy()
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, read_loop)

async def recognize_and_send(session: aiohttp.ClientSession):
    global last_recognition_time, latest_frame
    while True:
        await asyncio.sleep(0.1)
        if time_mod.time() - last_recognition_time < RECOGNITION_INTERVAL:
            continue
        with frame_lock:
            if latest_frame is None:
                continue
            frame_copy = latest_frame.copy()

        loop = asyncio.get_running_loop()
        try:
            results = await loop.run_in_executor(
                executor,
                DeepFace.find,
                frame_copy, str(IMGS_PATH), False, True, "ArcFace", "cosine"
            )
            if results and len(results) > 0 and len(results[0]) > 0:
                best = results[0].iloc[0]
                name = os.path.basename(best["identity"]).rsplit(".", 1)[0]
                distance = best["distance"]
                print(f"Найден {name} с distance={distance}")
                if distance <= DISTANCE_THRESHOLD:
                    now = datetime.now()
                    wd = now.weekday() + 1
                    lesson = get_current_lesson(wd, now.time())
                    current_status, final_status = update_student_status(name, now, lesson)
                    payload = {
                        "id": name,
                        "status": current_status,
                        "final_status": final_status,
                        "time": now.strftime("%H:%M:%S"),
                        "schedule_id": lesson[0] if lesson else None,
                        "lesson_key": (lesson[1].strftime("%H:%M:%S"), lesson[2].strftime("%H:%M:%S")) if lesson else None
                    }
                    if name not in last_seen or time_mod.time() - last_seen[name] > COOLDOWN_PER_PERSON:
                        print(f"Отправка {payload}")
                        try:
                            async with session.post(FASTAPI_URL, json=payload) as resp:
                                text = await resp.text()
                                print(f"Ответ FastAPI: {resp.status} {text}")
                        except Exception as e:
                            print(f"Ошибка при POST: {e}")
                        last_seen[name] = time_mod.time()
        except Exception as e:
            print(f"DeepFace ошибка: {e}")
        last_recognition_time = time_mod.time()

async def display_video():
    global latest_frame
    while True:
        with frame_lock:
            if latest_frame is None:
                await asyncio.sleep(0.01)
                continue
            frame_copy = latest_frame.copy()
        cv2.imshow("Камера", frame_copy)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        await asyncio.sleep(0.01)

# -------------------------- Main --------------------------

async def main():
    await database.connect()
    await load_schedule()

    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        print("Не удалось подключиться к RTSP")
        return

    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            capture_frames(cap),
            recognize_and_send(session),
            display_video()
        )

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    asyncio.run(main())
