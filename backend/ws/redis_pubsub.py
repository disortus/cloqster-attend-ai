import json
import aioredis

redis = None

async def init_redis():
    global redis
    redis = await aioredis.from_url(
        "redis://localhost:6379",
        decode_responses=True
    )


async def publish_attend(event: dict):
    """
    Публикуем событие о посещаемости.
    """
    await redis.publish("attends", json.dumps(event))