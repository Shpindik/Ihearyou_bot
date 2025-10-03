"""Административные эндпоинты API (требуют JWT аутентификации)."""

from fastapi import APIRouter

from .admin_user import router as admin_user_router
from .analytics import router as analytics_router
from .auth import router as auth_router
from .menu import router as menu_router
from .message_template import router as message_template_router
from .notification import router as notification_router
from .question import router as question_router
from .telegram_user import router as telegram_user_router


# Создание административного роутера
router = APIRouter(prefix="/admin")

# Подключение всех административных подроутеров
router.include_router(auth_router)
router.include_router(admin_user_router)
router.include_router(telegram_user_router)
router.include_router(menu_router)
router.include_router(question_router)
router.include_router(analytics_router)
router.include_router(notification_router)
router.include_router(message_template_router)
