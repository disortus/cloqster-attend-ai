# Используем официальный образ как базу
FROM redis:latest

# Копируем свой конфиг
COPY redis.conf /home/disortus/fastcloq/redis-docker/redis.conf

# Запускаем Redis с нашим конфигом
CMD ["redis-server", "/home/disortus/fastcloq/redis-docker/redis.conf"]