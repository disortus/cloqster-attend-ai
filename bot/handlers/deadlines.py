from aiogram import Router
from aiogram import Bot

router = Router()

async def notify_curator(event: dict, bot: Bot):
    curator_id = event["curator_id"]

    absents = event["absent"]
    lates = event["late"]

    text = "⏰ Прошло 5 минут с начала урока.\n"

    if absents:
        text += "\n❌ Не пришли:\n" + "\n".join(
            f"- {a['fullname']}" for a in absents
        )

    if lates:
        text += "\n⏱ Опоздали:\n" + "\n".join(
            f"- {l['fullname']} ({l['come_at']})" for l in lates
        )

    await bot.send_message(curator_id, text)
