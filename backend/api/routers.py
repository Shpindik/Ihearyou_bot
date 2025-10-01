"""Централизованное подключение всех роутеров API."""

from fastapi import APIRouter

from .v1.admin.analytics import router as admin_analytics_router

# Административные эндпоинты (с JWT)
from .v1.admin.auth import router as admin_auth_router
from .v1.admin.menu import router as admin_menu_router
from .v1.admin.notification import router as admin_notifications_router
from .v1.admin.question import router as admin_questions_router
from .v1.admin.reminder_template import router as admin_reminder_templates_router
from .v1.admin.user import router as admin_users_router

# Bot API эндпоинты
from .v1.bot.reminder import router as bot_reminder_router
from .v1.bot.telegram_user import router as bot_telegram_user_router

# Публичные эндпоинты (без JWT)
from .v1.public.menu import router as public_menu_router
from .v1.public.ratings import router as public_ratings_router
from .v1.public.search import router as public_search_router
from .v1.public.user_activity import router as public_user_activities_router
from .v1.public.user_question import router as public_user_questions_router


# Создание главного роутера API
api_router = APIRouter(prefix="/api/v1")

# Подключение Bot API эндпоинтов
api_router.include_router(bot_telegram_user_router, prefix="/bot")
api_router.include_router(bot_reminder_router, prefix="/bot")

# Подключение публичных эндпоинтов (без JWT)
api_router.include_router(public_menu_router)
api_router.include_router(public_search_router)
api_router.include_router(public_user_activities_router)
api_router.include_router(public_user_questions_router)
api_router.include_router(public_ratings_router)

# Подключение административных эндпоинтов (с JWT)
api_router.include_router(admin_auth_router)
api_router.include_router(admin_users_router)
api_router.include_router(admin_menu_router)
api_router.include_router(admin_questions_router)
api_router.include_router(admin_analytics_router)
api_router.include_router(admin_notifications_router)
api_router.include_router(admin_reminder_templates_router)
