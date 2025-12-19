from redis.asyncio import Redis
import json

redis = Redis()

async def publish_event(channel: str, data: dict):
    await redis.publish(channel, json.dumps(data))
