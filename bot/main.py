import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from handlers import router
from reminders import send_reminders


load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "bot_errors.log")

os.makedirs(LOG_DIR, exist_ok=True)


def check_tokens():
    """Check if all required environment variables are set"""
    missing_tokens = [
        name
        for name, value in {
            "TOKEN": BOT_TOKEN,
        }.items()
        if not value
    ]
    if missing_tokens:
        logging.critical(
            f"Отсутствуют обязательные переменные окружения: \
                         {', '.join(missing_tokens)}"
        )
    return not missing_tokens


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

scheduler = AsyncIOScheduler()


async def main():
    print("Бот запущен. Для остановки нажмите Ctrl+C.")

    await bot.delete_webhook(drop_pending_updates=True)
    polling_task = asyncio.create_task(dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types()))

    # поставил 15 sec для теста, сменить на время дня
    scheduler.add_job(send_reminders, "interval", seconds=15, args=[BOT_TOKEN])
    scheduler.start()

    def shutdown():
        polling_task.cancel()
        scheduler.shutdown()

    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_event_loop().add_signal_handler(sig, shutdown)

    try:
        await polling_task
    except asyncio.CancelledError:
        pass


console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setLevel(logging.ERROR)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, handlers=[console_handler, file_handler])
    asyncio.run(main())
