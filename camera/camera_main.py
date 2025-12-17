import cv2
import os
from postgres import database
from concurrent.futures import ThreadPoolExecutor
import requests
import time
from datetime import datetime
from deepface import DeepFace
from pathlib import Path
import threading
import asyncio
import aiohttp

BASE_DIR = Path(__file__).resolve().parent.parent
IMGS_PATH = BASE_DIR / 'backend' / 'databases' / 'imgs'
FASTAPI_URL = "http://localhost:5000/recognize"
RTSP_URL = "rtsp://disortus:new_pass125@192.168.1.101:554/stream1"
RECOGNITION_INTERVAL = 2.0
DISTANCE_THRESHOLD = 1
COOLDOWN_PER_PERSON = 10
STATE_TIMEOUT = 15  # секунд — если не видели >15 сек во время урока → left

cache_lock = threading.Lock()
frame_lock = threading.Lock()
latest_frame = None
last_recognition_time = 0

#     "student_id": {
#         "current_status": "present/left/absent",
#         "final_status": "present/late/absent",   # ← Новый: фиксированный на урок
#         "last_seen": timestamp,
#         "lesson_key": (weekday, (start_time, end_time)),
#         "first_seen_during_lesson": timestamp | None  # Для определения опоздания
#     }
# }

student_state = {}  # {student_id: {"status": str, "last_seen": float, "lesson_key": tuple | None}}
schedule_cache = {}
lesson_cache = {}
last_seen = {}

executor = ThreadPoolExecutor(max_workers=2)

async def load_schedule():
    global schedule_cache
    async with database.pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, weekday, start_time, end_time FROM Schedules ORDER BY weekday, start_time")
        # rows2 = await conn.fetch("SELECT id FROM Lessons WHERE schedule_id = $1 AND ")
    
    new_cache = {}
    for row in rows:
        weekday = row['weekday']
        if weekday not in new_cache:
            new_cache[weekday] = []
        new_cache[weekday].append((row['id'], row['start_time'], row['end_time']))
    
    with cache_lock:
        schedule_cache = new_cache
    print(f"Расписание загружено: {len(rows)} записей")

async def schedule_refresher():
    while True:
        await load_schedule()
        await asyncio.sleep(6 * 3600)

def get_current_lesson(weekday: int, cur_time: time) -> tuple | None:
    """
    Возвращает (schedule_id, start_time, end_time) или None
    """
    with cache_lock:
        lessons = schedule_cache.get(weekday, [])
    
    for sched_id, start, end in lessons:
        if start <= cur_time <= end:
            return (sched_id, start, end)
    return None

def update_student_status(student_id: str, now: datetime, current_lesson: tuple | None):
    global student_state
    
    current_time = time.time()
    lesson_key = current_lesson  # (start, end) или None
    
    state = student_state.get(student_id, {
        "current_status": "absent",
        "final_status": "absent",
        "last_seen": 0,
        "lesson_key": None,
        "first_seen_during_lesson": None
    })
    
    # Смена урока — полный сброс
    if state["lesson_key"] != lesson_key:
        state = {
            "current_status": "absent",
            "final_status": "absent",
            "last_seen": 0,
            "lesson_key": lesson_key,
            "first_seen_during_lesson": None
        }
    
    # Если сейчас идёт урок
    if current_lesson:
        start_time, end_time = current_lesson
        
        # Первый раз видим на этом уроке — фиксируем опоздание
        if state["first_seen_during_lesson"] is None:
            if now.time() > start_time:  # Пришёл после начала
                state["final_status"] = "late"
                print(f"⚠ {student_id} опоздал на урок")
            else:
                state["final_status"] = "present"
            state["first_seen_during_lesson"] = current_time
        
        # Обновляем текущее положение
        state["current_status"] = "present"
        state["last_seen"] = current_time
        print(f"→ {student_id} присутствует (итоговый статус: {state['final_status']})")
    
    student_state[student_id] = state
    
    # Возвращаем ТЕКУЩИЙ статус для отправки (present/left)
    return state["current_status"], state["final_status"]

async def check_absent_during_lesson(session: aiohttp.ClientSession):
    while True:
        await asyncio.sleep(10)
        
        now = datetime.now()
        weekday = now.weekday()
        cur_time = now.time().replace(microsecond=0)
        current_lesson = get_current_lesson(weekday, cur_time)
        
        if not current_lesson:
            await asyncio.sleep(10)
            continue
        
        current_time = time.time()
        to_update = []
        
        for sid, state in list(student_state.items()):
            if (state["lesson_key"] == current_lesson and
                state["current_status"] == "present" and
                current_time - state["last_seen"] > STATE_TIMEOUT):
                
                state["current_status"] = "left"
                print(f"← {sid} вышел с урока (итоговый: {state['final_status']})")
                to_update.append((sid, "left", now.strftime("%H:%M:%S"), state["final_status"]))
        
        # Отправляем в FastAPI
        for sid, curr_status, t, final_status in to_update:
            payload = {
                "id": sid,
                "status": curr_status,        # left
                "time": t,
                "final_status": final_status  # ← можно отправлять, если нужно в БД
            }
            try:
                async with session.post(FASTAPI_URL, json=payload):
                    print(payload)
            except Exception as e:
                print(f"except: {e}")

def get_status_from_cache(cur_time: time, weekday: int) -> str:
    with cache_lock:
        lessons = schedule_cache.get(weekday, [])
    
    if not lessons:
        return "present"  # Или дефолт
    
    for start, end in lessons:
        if start <= cur_time <= end:
            # Если текущее время > start + допустимое опоздание (например 15 мин)
            # Здесь упрощённо: если час >= start.hour +1 или после start
            if cur_time > start:  # Подстрой под логику
                return "late"
            return "present"
    
    return "present"  # Вне урока — present или другой статус

async def capture_frames(cap: cv2.VideoCapture):
    """Фоновый захват кадров с RTSP в отдельном потоке"""
    global latest_frame

    def read_loop():
        nonlocal cap
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Не удалось получить кадр (возможно, конец потока или ошибка RTSP)")
                time.sleep(0.1)  # Не грузим CPU при ошибке
                continue
            with frame_lock:
                latest_frame = frame.copy()
            # Никакого asyncio.sleep(0) или get_event_loop() не нужно!
            # Просто продолжаем цикл быстро

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, read_loop)

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
                name = os.path.basename(best["identity"]).rsplit(".", 1)[0]
                distance = best["distance"]
                
                if distance < DISTANCE_THRESHOLD:
                    now = datetime.now()
                    time_str = now.strftime("%H:%M:%S")
                    weekday = now.weekday()
                    cur_time = now.time().replace(microsecond=0)
                    
                    current_lesson = get_current_lesson(weekday, cur_time)
                    current_status, final_status = update_student_status(name, now, current_lesson)

                    if current_lesson:
                        start_str = current_lesson[1].strftime("%H:%M:%S")
                        end_str = current_lesson[2].strftime("%H:%M:%S")
                        lesson_key = (weekday, (start_str, end_str)) # Или просто кортеж как строка
                        schedule_id = current_lesson[0]
                    else:
                        lesson_key = None
                        schedule_id = None

                    time_str = now.strftime("%H:%M:%S")

                    # Формируем payload с lesson_key
                    payload = {
                        "id": name,
                        "status": current_status,           # present / left
                        "time": time_str,
                        "final_status": final_status,       # late / present / absent
                        "lesson_key": lesson_key,          # ← Новый поле!
                        "schedule_id": schedule_id
                    }

                    # Отправляем (с cooldown)
                    if name not in last_seen or time.time() - last_seen[name] > COOLDOWN_PER_PERSON:
                        try:
                            async with session.post(FASTAPI_URL, json=payload) as resp:
                                if resp.status == 200:
                                    print(f"✅ Отправлено: {name} | {current_status} | урок: {lesson_key}")
                                else:
                                    print(f"Ошибка ответа: {resp.status}")
                        except Exception as e:
                            print(f"Не удалось отправить: {e}")
    
                        last_seen[name] = time.time()
        except Exception as e:
            print(f"Ошибка: {e}")
        
        last_recognition_time = time.time()

async def display_video():
    global latest_frame
    while True:
        with frame_lock:
            if latest_frame is not None:
                display_frame = latest_frame.copy()
            else:
                await asyncio.sleep(0.01)
                continue
        
        cv2.putText(display_frame, "Асинхронная камера + кэш расписания", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow('RTSP Camera', display_frame)
        
        if cv2.waitKey(1) == ord('q'):
            break
        await asyncio.sleep(0.01)

async def main():
    await database.connect()
    await load_schedule()  # Первая загрузка
    
    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        print("Не удалось подключиться к RTSP")
        return
    
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            capture_frames(cap),
            recognize_and_send(session),
            display_video(),
            schedule_refresher(),  # Фоновая перезагрузка кэша
            check_absent_during_lesson() # Новая задача
        )
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    asyncio.run(main())