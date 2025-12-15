import asyncio
import cv2
import face_recognition
import requests
import time
from datetime import datetime
from .face_utils import load_known_encodings
from .config import  TOLERANCE, PROCESS_EVERY_N_FRAMES, ENCODINGS_RELOAD_INTERVAL, RTSP_URL, API_URL, AUD_ID

async def process_camera(aud_id: int):
    """
    Основной процессор для одной камеры: читает поток, распознаёт лица, отправляет обновления в API.
    """


    config = AUD_ID
    rtsp_url = RTSP_URL
    api_url = API_URL

    # Инициализация
    known_encodings, known_student_ids = await load_known_encodings()
    last_reload_time = time.time()

    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        raise RuntimeError(f"Ошибка подключения к камере по {rtsp_url}")

    frame_count = 0
    try:
        while True:
            # Перезагрузка encodings периодически
            if time.time() - last_reload_time > ENCODINGS_RELOAD_INTERVAL:
                known_encodings, known_student_ids = await load_known_encodings()
                last_reload_time = time.time()
                print(f"Encodings перезагружены для aud_id {aud_id}")

            ret, frame = cap.read()
            if not ret:
                print(f"Потеря фрейма для aud_id {aud_id}, переподключение...")
                time.sleep(1)
                cap.release()
                cap = cv2.VideoCapture(rtsp_url)
                continue

            frame_count += 1
            if frame_count % PROCESS_EVERY_N_FRAMES != 0:
                continue  # Пропускаем фреймы для оптимизации

            # Уменьшаем размер фрейма для скорости (1/4)
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Находим лица и encodings
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for face_encoding in face_encodings:
                # Сравниваем с известными
                matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=TOLERANCE)
                if True in matches:
                    first_match_index = matches.index(True)
                    student_id = known_student_ids[first_match_index]

                    # Отправляем в API
                    now = datetime.now().isoformat()
                    payload = {
                        "aud_id": aud_id,
                        "student_id": student_id,
                        "timestamp": now
                    }
                    try:
                        response = requests.post(api_url, json=payload)
                        if response.status_code == 200:
                            print(f"Обновлено для student_id {student_id} в aud_id {aud_id}")
                        else:
                            print(f"Ошибка API: {response.status_code} - {response.text}")
                    except Exception as e:
                        print(f"Ошибка отправки в API: {e}")

            # Опционально: для дебага, показать видео (убери в проде)
            # cv2.imshow(f"Camera {aud_id}", frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

            await asyncio.sleep(0)  # Чтобы не блокировать event loop
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":

    asyncio.run(process_camera())