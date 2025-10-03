"""Bot API эндпоинты (внутренний API для Telegram бота)."""

from fastapi import APIRouter

from .message_template import router as message_template_router
from .telegram_user import router as telegram_user_router


# Создание bot роутера
router = APIRouter(prefix="/bot")

# Подключение всех bot подроутеров
router.include_router(telegram_user_router)
router.include_router(message_template_router)
