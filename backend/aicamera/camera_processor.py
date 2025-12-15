import asyncio
import cv2
import face_recognition
import requests
import time
from datetime import datetime
from .face_utils import load_known_encodings
from .config import (
    RTSP_URL,
    API_URL,
    AUD_ID,
    TOLERANCE,
    PROCESS_EVERY_N_FRAMES,
    ENCODINGS_RELOAD_INTERVAL,
)

async def main():
    print(f"Запуск системы распознавания для аудитории ID={AUD_ID}")
    print(f"Подключение к камере: {RTSP_URL}")

    # Первоначальная загрузка известных лиц
    known_encodings, known_student_ids = await load_known_encodings()
    last_reload_time = time.time()

    # Подключение к видеопотоку
    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        print("ОШИБКА: Не удалось подключиться к камере! Проверь RTSP_URL в config.py")
        return

    frame_count = 0
    try:
        while True:
            # Перезагружаем encodings, если прошло много времени
            if time.time() - last_reload_time > ENCODINGS_RELOAD_INTERVAL:
                print("Перезагружаем список известных лиц из БД...")
                known_encodings, known_student_ids = await load_known_encodings()
                last_reload_time = time.time()

            ret, frame = cap.read()
            if not ret:
                print("Потеря соединения с камерой. Пытаюсь переподключиться...")
                cap.release()
                time.sleep(2)
                cap = cv2.VideoCapture(RTSP_URL)
                continue

            frame_count += 1
            if frame_count % PROCESS_EVERY_N_FRAMES != 0:
                continue  # Пропускаем кадры для оптимизации

            # Уменьшаем кадр в 4 раза — сильно ускоряет обработку
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Поиск лиц и вычисление encodings
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(
                    known_encodings, face_encoding, tolerance=TOLERANCE
                )
                if True in matches:
                    match_index = matches.index(True)
                    student_id = known_student_ids[match_index]

                    # Формируем и отправляем данные на сервер
                    payload = {
                        "aud_id": AUD_ID,
                        "student_id": student_id,
                        "timestamp": datetime.now().isoformat()
                    }
                    try:
                        response = requests.post(API_URL, json=payload, timeout=5)
                        if response.status_code == 200:
                            print(f"✓ Студент {student_id} отмечен как присутствующий")
                        else:
                            print(f"✗ Сервер вернул ошибку: {response.status_code}")
                    except requests.RequestException as e:
                        print(f"✗ Не удалось отправить данные на сервер: {e}")

            # Небольшая пауза, чтобы не грузить CPU на 100%
            await asyncio.sleep(0.01)

    except KeyboardInterrupt:
        print("\nОстановка обработки камеры пользователем...")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Камера отключена. До свидания!")

if __name__ == "__main__":
    asyncio.run(main())