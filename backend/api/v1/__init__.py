"""Инициализация v1 API."""

from fastapi import APIRouter

from .admin import router as admin_router
from .bot import router as bot_router
from .public import router as public_router


# Создание главного роутера v1
api_v1_router = APIRouter(prefix="/api/v1")

# Подключение всех подроутеров
api_v1_router.include_router(admin_router)
api_v1_router.include_router(bot_router)
api_v1_router.include_router(public_router)
