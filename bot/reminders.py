import os
from asyncio import sleep

from aiogram import Bot
from api_client import APIClient


bot = Bot(token=os.getenv("BOT_TOKEN"))


async def send_reimnders():
    async with APIClient() as api:
        users = await api.get_inactive_users()

    for user in users:
        try:
            await bot.send_message(user["id"], f"Привет, {user['first_name']}. Ты давно не появлялся у нас!")
            print(f"Reminder sent to {user['id']}")
        except Exception as e:
            print(f"Ошибка отправки напоминания: {e}")

        await sleep(0.5)
