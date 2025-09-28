"""Административные эндпоинты для управления пользователями Telegram."""

from fastapi import APIRouter, Depends, Query, status
from fastapi.security import HTTPBearer

from schemas.admin.user import (
    AdminTelegramUserResponse,
    AdminTelegramUserListResponse,
)

router = APIRouter(prefix="/admin/telegram-users", tags=["Admin Telegram Users"])
security = HTTPBearer()


@router.get("/", response_model=AdminTelegramUserListResponse, status_code=status.HTTP_200_OK)
async def get_telegram_users(
    page: int = Query(1, description="Номер страницы (по умолчанию 1)"),
    limit: int = Query(20, description="Количество записей на странице (по умолчанию 20)"),
    search: str = Query(None, description="Поиск по имени или username"),
    subscription_type: str = Query(None, description="Фильтр по типу подписки (free, premium)"),
    token: str = Depends(security)
) -> AdminTelegramUserListResponse:
    """
    Получение списка пользователей Telegram.
    
    GET /api/v1/admin/telegram-users
    Требует: Authorization: Bearer <token>
    """
    pass


@router.get("/{id}", response_model=AdminTelegramUserResponse, status_code=status.HTTP_200_OK)
async def get_telegram_user(
    id: int,
    token: str = Depends(security)
) -> AdminTelegramUserResponse:
    """
    Получение информации о конкретном пользователе.
    
    GET /api/v1/admin/telegram-users/{id}
    Требует: Authorization: Bearer <token>
    """
    pass
