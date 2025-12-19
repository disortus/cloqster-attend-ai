import cv2
import os
import time
from datetime import datetime
from pathlib import Path
import threading
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from deepface import DeepFace

# =================== Настройки ===================
BASE_DIR = Path(__file__).resolve().parent.parent
IMGS_PATH = BASE_DIR / 'backend' / 'databases' / 'imgs'
FASTAPI_URL = "http://localhost:5000/camera/mark"
RTSP_URL = "rtsp://disortus:new_pass125@10.200.6.80:554/stream1"
RECOGNITION_INTERVAL = 2.0
DISTANCE_THRESHOLD = 0.4   # подстрой под свой ArcFace
COOLDOWN_PER_PERSON = 5    # секунд
STATE_TIMEOUT = 15         # секунд для left

executor = ThreadPoolExecutor(max_workers=2)
frame_lock = threading.Lock()
latest_frame = None
last_recognition_time = 0
last_seen = {}  # cooldown для каждого студента

# student_state: {id: {"current_status", "final_status", "last_seen", "lesson_key", "first_seen_during_lesson"}}
student_state = {}
schedule_cache = {}  # {weekday: [(schedule_id, start_time, end_time)]}
cache_lock = threading.Lock()

# =================== Загрузка расписания ===================
async def load_schedule():
    from postgres import database
    global schedule_cache
    async with database.pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, weekday, start_time, end_time FROM Schedules")
    new_cache = {}
    for r in rows:
        wd = r['weekday']
        new_cache.setdefault(wd, []).append((r['id'], r['start_time'], r['end_time']))
    with cache_lock:
        schedule_cache = new_cache
    print(f"Расписание загружено: {len(rows)} записей")

async def schedule_refresher():
    while True:
        await load_schedule()
        await asyncio.sleep(6*3600)

# =================== Получение текущего урока ===================
def get_current_lesson(weekday: int, cur_time: time):
    with cache_lock:
        lessons = schedule_cache.get(weekday, [])
    for schedule_id, start, end in lessons:
        if start <= cur_time <= end:
            return schedule_id, start, end
    return None

# =================== Обновление статуса студента ===================
def update_student_status(student_id: str, now: datetime, current_lesson: tuple):
    """Возвращает current_status и final_status"""
    current_time = time.time()
    lesson_key = current_lesson  # (schedule_id, start, end) или None

    state = student_state.get(student_id, {
        "current_status": "absent",
        "final_status": "absent",
        "last_seen": 0,
        "lesson_key": None,
        "first_seen_during_lesson": None
    })

    # смена урока — сброс
    if state["lesson_key"] != lesson_key:
        state["current_status"] = "absent"
        state["final_status"] = "absent"
        state["last_seen"] = 0
        state["lesson_key"] = lesson_key
        state["first_seen_during_lesson"] = None

    # если сейчас урок
    if current_lesson:
        schedule_id, start_time, end_time = current_lesson
        # первый раз видим на этом уроке — фиксируем late/present
        if state["first_seen_during_lesson"] is None:
            if now.time() > start_time:
                state["final_status"] = "late"
            else:
                state["final_status"] = "present"
            state["first_seen_during_lesson"] = current_time
        state["current_status"] = "present"
        state["last_seen"] = current_time

    # если студент ушёл и вернулся — сохраняем final_status
    student_state[student_id] = state
    return state["current_status"], state["final_status"]

# =================== Проверка ушедших ===================
async def check_left(session: aiohttp.ClientSession):
    while True:
        await asyncio.sleep(10)
        now = datetime.now()
        weekday = now.weekday()
        cur_time = now.time()
        current_lesson = get_current_lesson(weekday, cur_time)
        if not current_lesson:
            continue

        to_update = []
        for sid, state in list(student_state.items()):
            if state["lesson_key"] == current_lesson and state["current_status"] == "present":
                if time.time() - state["last_seen"] > STATE_TIMEOUT:
                    state["current_status"] = "left"
                    to_update.append((sid, "left", state["final_status"]))
        # отправка в FastAPI
        for sid, curr_status, final_status in to_update:
            payload = {
                "id": sid,
                "status": curr_status,
                "time": datetime.now().strftime("%H:%M:%S"),
                "final_status": final_status
            }
            try:
                async with session.post(FASTAPI_URL, json=payload):
                    print(f"LEFT обновлено: {payload}")
            except Exception as e:
                print(f"Ошибка отправки left: {e}")

# =================== Захват кадров ===================
async def capture_frames(cap: cv2.VideoCapture):
    global latest_frame
    def loop():
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                with frame_lock:
                    latest_frame = frame.copy()
            else:
                time.sleep(0.1)
    loop_ = asyncio.get_running_loop()
    await loop_.run_in_executor(None, loop)

# =================== Распознавание лиц и отправка ===================
async def recognize_and_send(session: aiohttp.ClientSession):
    global last_recognition_time, latest_frame
    while True:
        await asyncio.sleep(0.1)
        if time.time() - last_recognition_time < RECOGNITION_INTERVAL:
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
                frame_copy, IMGS_PATH, False, True, "ArcFace", "cosine"
            )
            if results and len(results) > 0 and len(results[0]) > 0:
                best = results[0].iloc[0]
                name = os.path.basename(best["identity"]).rsplit(".",1)[0]
                distance = best["distance"]
                if distance < DISTANCE_THRESHOLD:
                    now = datetime.now()
                    weekday = now.weekday()
                    cur_time = now.time()
                    current_lesson = get_current_lesson(weekday, cur_time)
                    current_status, final_status = update_student_status(name, now, current_lesson)
                    payload = {
                        "id": name,
                        "status": current_status,
                        "time": now.strftime("%H:%M:%S"),
                        "final_status": final_status,
                        "schedule_id": current_lesson[0] if current_lesson else None
                    }
                    if name not in last_seen or time.time() - last_seen[name] > COOLDOWN_PER_PERSON:
                        try:
                            async with session.put(FASTAPI_URL, json=payload) as resp:
                                print(f"Отправлено: {payload} | {resp.status}")
                        except Exception as e:
                            print(f"Ошибка отправки: {e}")
                        last_seen[name] = time.time()
        except Exception as e:
            print(f"Ошибка распознавания: {e}")
        last_recognition_time = time.time()

# =================== Отображение видео ===================
async def display_video():
    global latest_frame
    while True:
        with frame_lock:
            if latest_frame is not None:
                frame = latest_frame.copy()
            else:
                await asyncio.sleep(0.01)
                continue
        # cv2.imshow("Camera", frame)
        # if cv2.waitKey(1) == ord('q'):
        #     break
        await asyncio.sleep(0.01)

# =================== Главная функция ===================
async def main():
    import postgres as db
    await db.database.connect()
    await load_schedule()
    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        print("Не удалось подключиться к RTSP")
        return
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            capture_frames(cap),
            recognize_and_send(session),
            display_video(),
            schedule_refresher(),
            check_left(session)
        )
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    asyncio.run(main())
