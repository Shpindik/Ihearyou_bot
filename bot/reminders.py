import logging
from asyncio import sleep

from aiogram import Bot
from api_client import APIClient


async def send_reminders(bot_token):
    async with APIClient() as api:
        template_data = await api.get_reminder_template()
    
    if not template_data:
        print("Не удалось отправить напоминания.")
        return
    message = template_data.get("message_template")
    days = template_data.get("inactive_days", 10)

    async with APIClient() as api:
        users_json = await api.get_inactive_users(days=days)
    users = users_json.get("users", [])
    if users:
        bot = Bot(token=bot_token)
        for user in users:
            try:
                await bot.send_message(
                    user["telegram_id"], message)
                print(f"Reminder sent to {user['id']}")
            except Exception as e:
                print(f"Ошибка отправки напоминания: {e}")

        await sleep(0.5)
