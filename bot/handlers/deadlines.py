from aiogram import Bot

bot = Bot("TOKEN")

async def notify_curator(event: dict):
    curator_id = event["curator_id"]

    absents = event["absent"]
    lates = event["late"]

    text = "⏰ Прошло 5 минут.\n"

    if absents:
        text += "\nНе пришли:\n" + "\n".join(f"- {a['fullname']}" for a in absents)

    if lates:
        text += "\nОпоздали:\n" + "\n".join(f"- {l['fullname']} ({l['come_at']})" for l in lates)

    await bot.send_message(curator_id, text)
