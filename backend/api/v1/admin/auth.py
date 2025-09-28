"""Эндпоинты аутентификации администраторов."""

from fastapi import APIRouter, status

from schemas.admin.auth import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminRefreshRequest,
    AdminRefreshResponse,
)

router = APIRouter(prefix="/admin/auth", tags=["Admin Auth"])


@router.post("/login", response_model=AdminLoginResponse, status_code=status.HTTP_200_OK)
async def login_admin(
    request: AdminLoginRequest
) -> AdminLoginResponse:
    """
    Аутентификация администратора.
    
    POST /api/v1/admin/auth/login
    Возвращает JWT токены для доступа к административным функциям
    """
    pass


@router.post("/refresh", response_model=AdminRefreshResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    request: AdminRefreshRequest
) -> AdminRefreshResponse:
    """
    Обновление токена доступа.
    
    POST /api/v1/admin/auth/refresh
    Обновляет истекший access token с помощью refresh token
    """
    pass
