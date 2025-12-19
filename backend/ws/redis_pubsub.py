import json
from redis.asyncio import Redis

redis = Redis(host="localhost", port=6379, decode_responses=True)


async def publish_attend(event: dict, channel: str = "attends"):
    await redis.publish(channel, json.dumps(event))


async def subscribe(channel: str = "attends"):
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)
    return pubsub
