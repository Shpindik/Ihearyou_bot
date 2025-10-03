"""Публичные эндпоинты API (без JWT аутентификации)."""

from fastapi import APIRouter

from .menu import router as menu_router
from .question import router as question_router
from .ratings import router as ratings_router
from .search import router as search_router
from .user_activity import router as user_activity_router


# Создание публичного роутера
router = APIRouter(prefix="/public", tags=["Public"])

# Подключение всех публичных подроутеров
router.include_router(menu_router)
router.include_router(search_router)
router.include_router(user_activity_router)
router.include_router(question_router)
router.include_router(ratings_router)
