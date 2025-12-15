# Конфигурация для камеры — только одна камера в учебном проекте

# ID аудитории, где стоит камера (из таблицы Audience.id)
AUD_ID = 1

# RTSP-адрес твоей IP-камеры. Замени на реальный!
# Пример: rtsp://login:password@192.168.1.50:554/streaming/channel/1
RTSP_URL = "rtsp://disortus:new_pass125@192.168.1.101:554/stream1"

# URL эндпоинта в твоём FastAPI, куда отправлять данные о распознанных студентах
API_URL = "http://localhost:5000/api/aicamera/update"

# Параметры распознавания лиц
TOLERANCE = 0.6  # Чем меньше — тем строже совпадение (0.6 — оптимально)
PROCESS_EVERY_N_FRAMES = 5  # Обрабатывать каждый 5-й кадр (экономит CPU)

# Как часто перезагружать список лиц из БД (на случай, если куратор добавил новое фото)
ENCODINGS_RELOAD_INTERVAL = 300  # 300 секунд = 5 минут

# Строка подключения к PostgreSQL (замени на свою)
# Формат: postgresql://user:password@host:port/dbname

