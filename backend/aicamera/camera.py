from deepface import DeepFace
import cv2
import numpy as np
import time

# cap = cv2.VideoCapture("rtcp://disortus:new_pass125@192.168.0.19:554/stream1")
cap = ...

while True:
    ret, frame = ..., ... #cap.read()
    print(ret)
    if not ret:
        continue

    try:
        result = DeepFace.find(
            img_path=frame,
            db_path="faces_db/",
            model_name="ArcFace",
            detector_backend="mediapipe",
            enforce_detection=False
        )
        print(result)

        if len(result) > 0:
            match = result[0].iloc[0]
            identity = match['identity']
            print(match)

    except Exception:
        pass
