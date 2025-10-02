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

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "bot_errors.log")

os.makedirs(LOG_DIR, exist_ok=True)

# Добавляем PyLogPath в PYTHONPATH для импорта backend модулей
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)


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
            f'Отсутствуют обязательные переменные окружения: \
                         {", ".join(missing_tokens)}'
        )
    return not missing_tokens


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

# Инициализация планировщика задач
scheduler = AsyncIOScheduler()


def setup_scheduler():
    """Настройка MVP планировщика для ежедневных напоминаний в 10:00."""
    try:
        from scheduler_tasks import (
            send_reminders_cron,
            cleanup_old_notifications,
            notification_statistics_report,
            health_check_notifications,
        )
        
        # MVP главная задача: ежедневная отправка напоминаний в 10:00 утра
        scheduler.add_job(
            send_reminders_cron,
            trigger="cron",
            hour=10,
            minute=0,
            timezone="Europe/Moscow",  # UTC+3 для России
            id="mvp_send_reminders",
            name="MVP: Ежедневные напоминания в 10:00",
            max_instances=1,
            replace_existing=True,
        )
        
        # Очистка старых уведомлений каждую неделю по воскресеньям в 3:00
        scheduler.add_job(
            cleanup_old_notifications,
            trigger="cron",
            day_of_week="sun",
            hour=3,
            minute=0,
            timezone="Europe/Moscow",
            id="mvp_cleanup_notifications",
            name="MVP: Очистка старых уведомлений",
            max_instances=1,
            replace_existing=True,
        )
        
        # Статистика уведомлений каждый день в 20:00
        scheduler.add_job(
            notification_statistics_report,
            trigger="cron",
            hour=20,
            minute=0,
            timezone="Europe/Moscow",
            id="mvp_notification_stats",
            name="MVP: Статистика уведомлений",
            max_instances=1,
            replace_existing=True,
        )
        
        # Проверка здоровья каждый час
        scheduler.add_job(
            health_check_notifications,
            trigger="interval",
            minutes=60,
            id="mvp_health_check",
            name="MVP: Проверка здоровья системы",
            max_instances=1,
            replace_existing=True,
        )
        
        logging.info("📅 MVP Планировщик настроен: ежедневные напоминания в 10:00")
        
    except ImportError as e:
        logging.error(f"❌ MVP: Ошибка импорта задач: {str(e)}")
        raise




async def main():
    """Запуск упрощенного бота с напоминаниями."""
    print("🚀 Запуск Telegram бота с напоминаниями...")
    
    # Настройка планировщика
    try:
        setup_scheduler()
        scheduler.start()
        print("📅 Планировщик запущен")
    except Exception as e:
        print(f"❌ Ошибка планировщика: {e}")
    
    print("🤖 Бот запущен")
    
    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    polling_task = asyncio.create_task(
        dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    )

    def shutdown():
        """Завершение работы."""
        print("\n🛑 Завершение...")
        scheduler.shutdown(wait=False)
        polling_task.cancel()

    # Обработка сигналов завершения
    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_event_loop().add_signal_handler(sig, shutdown)

    try:
        await polling_task
    except asyncio.CancelledError:
        print("✅ Бот завершен")
    finally:
        scheduler.shutdown()


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
