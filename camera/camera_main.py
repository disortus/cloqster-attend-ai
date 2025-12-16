import cv2
#import face_recognition
import os
import requests
import time
from datetime import datetime
from deepface import DeepFace
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
IMGS_PATH = BASE_DIR / 'backend' / 'databases' / 'imgs'
FASTAPI_URL = "http://localhost:5000/recognize"

last_seen = {}
cap = cv2.VideoCapture("rtsp://disortus:new_pass125@192.168.1.101:554/stream1")

while True:
    try:
        ret, frame = cap.read()
        if not ret:
            break
        print("ret =", ret)
        try:
            # DeepFace.find возвращает список совпадений в базе
            results = DeepFace.find(img_path=frame, db_path=IMGS_PATH, enforce_detection=False, silent=True)
            print("Results:", results)

            if len(results) > 0 and len(results[0]) > 0:
                # Берём лучшее совпадение (первое — самое близкое)
                name = results[0].iloc[0]["identity"].split("/")[-1].split(".")[0]  # Имя из файла
                print("Matched name:", name)
                distance = results[0].iloc[0]["distance"]  # Чем меньше — тем лучше (порог ~0.3-0.4 для ArcFace)
                print("Distance:", distance)
                if distance < 1:  # Порог — подбери под свои фото
                    now = datetime.now()
                    print("Current time:", now)
                    time_str = now.strftime("%H:%M")
                    print("Formatted time:", time_str)
                    status = "пришёл вовремя" if now.hour < 9 else "опоздал"
                    print("Status:", status)

                    if name not in last_seen or time.time() - last_seen[name] > 30:
                        requests.post(FASTAPI_URL, json={"name": name, "status": status, "time": time_str})
                        last_seen[name] = time.time()
                        print(f"Отправлено: {name} — {status} в {time_str}")
                        print(f"Обнаружен: {name} — {status} (distance: {distance:.2f})")
                else:
                    name = "Неизвестный"
                    print("Distance too high, marked as unknown.")
            else:
                name = "Неизвестный"
                print("No matches found, marked as unknown.")

        except Exception as e:
            print(f"Ошибка распознавания: {e}")
            name = "Неизвестный"

        cv2.putText(frame, name, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        # cv2.imshow('Camera', frame)

        # if cv2.waitKey(1) == ord('q'):
        #   break
    except Exception as e:
        print(f"Ошибка захвата кадра: {e}")
        continue

cap.release()
