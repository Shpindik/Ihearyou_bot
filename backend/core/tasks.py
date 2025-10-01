from backend.core.celery_app import celery_app
import os
import requests


@celery_app.task(name="backend.tasks.send_telegram_message")
def send_telegram_message(chat_id: int, message: str) -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        return
    # Лёгкий синхронный вызов через aiogram здесь затруднён; используем HTTP запрос
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": message})
    except Exception:
        pass


