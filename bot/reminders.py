import logging
import os
from asyncio import sleep

from aiogram import Bot
from api_client import APIClient


async def send_reminders(bot_token):
    logging.debug("reminders job started")
    async with APIClient() as api:
        users_json = await api.get_inactive_users()
    logging.debug("users recieved")
    users = users_json.get("users", [])
    # users = [{"telegram_id": 1063349895, "first_name": "Val"}]
    if users:
        bot = Bot(token=bot_token)
        for user in users:
            try:
                await bot.send_message(
                    int(user["telegram_id"]), f"Привет, {user['first_name']}. Ты давно не появлялся у нас!"
                )
                print(f"Reminder sent to {user['id']}")
            except Exception as e:
                print(f"Ошибка отправки напоминания: {e}")

        await sleep(0.5)
