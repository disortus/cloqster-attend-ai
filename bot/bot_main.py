from aiogram import Bot, Dispatcher
from postgres import database
from handlers.deadlines import notify_curator
from redis.asyncio import Redis
from sqlites import init_db
import asyncio
import json

bot = Bot(token='8570799657:AAFYUAdPkpKEGbkyknmHn9qkdrhVamtzoh4')
dispatcher = Dispatcher()

async def redis_listener():
    redis = Redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe("deadline")

    while True:
        msg = await pubsub.get_message(ignore_subscribe_messages=True)
        if msg:
            event = json.loads(msg["data"])
            await notify_curator(event, bot)
        await asyncio.sleep(0.1)


async def main():
    await asyncio.gather(
        database.connect(),
        init_db(),
        dispatcher.start_polling(bot),
        redis_listener()
    )


if __name__ == "__main__":
    asyncio.run(main())