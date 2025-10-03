"""Основной файл Telegram бота."""

import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from .config import settings

# Импорт роутеров
from .handlers import menu, question, rating, search, start
from .middleware.logging import LoggingMiddleware
from .middleware.user_registration import UserRegistrationMiddleware
from .services.reminder_service import ReminderService


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("bot.log", encoding="utf-8")],
)

logger = logging.getLogger(__name__)


async def create_bot():
    """Создает и настраивает экземпляр бота."""
    if not settings.bot_token:
        raise ValueError("BOT_TOKEN не задан в переменных окружения")

    # Создаем экземпляры бота и диспетчера
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML, link_preview_is_disabled=settings.disable_web_page_preview
        ),
    )

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Создаем сервис напоминаний
    reminder_service = ReminderService(bot)

    # Подключаем middleware
    dp.message.middleware(UserRegistrationMiddleware())
    dp.callback_query.middleware(UserRegistrationMiddleware())
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    # Подключаем роутеры
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(search.router)
    dp.include_router(rating.router)
    dp.include_router(question.router)

    return bot, dp, reminder_service


async def on_startup(bot: Bot, reminder_service: ReminderService):
    """Обработчик запуска бота."""
    logger.info("Запускаем Telegram бот...")

    # Удаляем webhook если он был установлен
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url:
        await bot.delete_webhook()
        logger.info("Webhook удален")

    # Если указан webhook URL, устанавливаем его
    if settings.webhook_url:
        await bot.set_webhook(url=settings.webhook_url, secret_token=settings.webhook_secret)
        logger.info(f"Webhook установлен: {settings.webhook_url}")
    else:
        logger.info("Запуск в режиме polling")

    # Запускаем сервис напоминаний
    await reminder_service.start()
    logger.info("Сервис автоматических напоминаний запущен")

    logger.info("Бот успешно запущен!")


async def on_shutdown(bot: Bot, reminder_service: ReminderService):
    """Обработчик остановки бота."""
    logger.info("Останавливаем Telegram бот...")

    # Останавливаем сервис напоминаний
    await reminder_service.stop()
    logger.info("Сервис автоматических напоминаний остановлен")

    # Удаляем webhook перед остановкой
    await bot.delete_webhook(drop_pending_updates=True)

    # Закрываем соединения
    await bot.session.close()

    logger.info("Бот остановлен!")


async def startup_webhook(request: web.Request):
    """Обработчик webhook при запуске."""
    await on_startup(request.app["bot"], request.app["reminder_service"])
    return web.Response(text="OK")


def create_webhook_app(base_path: str = "/webhook") -> web.Application:
    """Создает приложение для webhook."""
    # Создаем экземпляры бота и диспетчера
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    bot, dp, reminder_service = loop.run_until_complete(create_bot())

    # Добавляем эндпоинты для webhook
    app = web.Application()
    app["bot"] = bot
    app["dp"] = dp
    app["reminder_service"] = reminder_service

    # Обработчик webhook
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=settings.webhook_secret)

    webhook_handler.register(app, path=base_path)

    # Эндпоинт для health check
    app.router.add_get("/health", lambda r: web.Response(text="OK"))

    # Эндпоинт для запуска (устанавливает webhook)
    app.router.add_post("/start", startup_webhook)

    # Настройка приложения
    setup_application(app, dp, bot=bot)

    return app


async def polling_mode():
    """Запуск бота в режиме polling."""
    try:
        bot, dp, reminder_service = await create_bot()

        # Создаем функции-обертки для регистрации обработчиков
        async def startup_handler():
            await on_startup(bot, reminder_service)

        async def shutdown_handler():
            await on_shutdown(bot, reminder_service)

        # Регистрируем обработчики запуска и остановки
        dp.startup.register(startup_handler)
        dp.shutdown.register(shutdown_handler)

        # Запускаем бота
        logger.info("Запускаем polling режим...")
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Ошибка в polling режиме: {e}")
        raise


async def webhook_mode():
    """Запуск бота в режиме webhook."""
    if not settings.webhook_url:
        raise ValueError("WEBHOOK_URL не задан для режима webhook")

    app = create_webhook_app()

    # Получаем порт из URL или используем стандартный
    try:
        from urllib.parse import urlparse

        parsed = urlparse(settings.webhook_url)
        port = parsed.port or 8080
    except Exception:
        port = 8080

    logger.info(f"Запускаем webhook режим на порту {port}...")

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logger.info(f"Webhook сервер запущен на порту {port}")

    # Держим сервер запущенным
    while True:
        await asyncio.sleep(3600)


async def main():
    """Основная функция запуска бота."""
    try:
        logger.info("Инициализация бота 'Я тебя слышу'...")

        # Определяем режим запуска
        if settings.webhook_url:
            await webhook_mode()
        else:
            await polling_mode()

    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Добавляем текущую директорию в Python path
    bot_dir = Path(__file__).parent
    project_dir = bot_dir.parent
    sys.path.insert(0, str(project_dir))

    # Запускаем бота
    asyncio.run(main())
