from aiogram import Bot, Dispatcher
from postgres import database
from sqlites import init_db
import asyncio

bot = Bot(token='8570799657:AAFYUAdPkpKEGbkyknmHn9qkdrhVamtzoh4')
dispatcher = Dispatcher()

async def main():
    await database.connect()
    await init_db()
    await dispatcher.start_polling(bot)
    

if __name__ == "__main__":
    asyncio.run(main())