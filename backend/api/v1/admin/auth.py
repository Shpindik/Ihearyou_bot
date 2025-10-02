"""Эндпоинты аутентификации администраторов."""

from datetime import timedelta

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.db import get_session
from backend.core.dependencies import ActiveAdmin
from backend.core.security import create_access_token, create_refresh_token
from backend.schemas.admin.auth import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminMeResponse,
    AdminPasswordResetConfirmRequest,
    AdminPasswordResetRequest,
    AdminPasswordResetSuccessResponse,
    AdminRefreshRequest,
    AdminRefreshResponse,
)
from backend.services.admin_user import admin_user_service
from backend.validators.admin_user import admin_user_validator


router = APIRouter(prefix="/admin/auth", tags=["Admin Auth"])


@router.post(
    "/login",
    response_model=AdminLoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Аутентификация администратора",
    description="Аутентификация администратора по имени пользователя и паролю",
    responses={
        200: {"description": "Аутентификация успешна, возвращены JWT токены"},
        400: {"description": "Ошибка валидации данных"},
        401: {"description": "Неверное имя пользователя или пароль"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def login_admin(
    request: AdminLoginRequest,
    session: AsyncSession = Depends(get_session),
) -> AdminLoginResponse:
    """Аутентификация администратора.

    Требует валидные учетные данные администратора.
    Возвращает JWT токены для доступа к административным функциям.
    Поддерживает вход по email или username.
    """
    admin = await admin_user_service.authenticate_admin_by_login_and_password(session, request.login, request.password)

    admin = admin_user_validator.validate_admin_authenticated(admin)
    admin = admin_user_validator.validate_admin_active(admin)

    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(admin.id), "username": admin.username, "role": admin.role},
        expires_delta=access_token_expires,
    )

    refresh_token = create_refresh_token(data={"sub": str(admin.id), "type": "refresh"})

    return AdminLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
    )


@router.post(
    "/refresh",
    response_model=AdminRefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновление токена доступа",
    description="Обновляет истекший access token с помощью refresh token",
    responses={
        200: {"description": "Токен доступа успешно обновлен"},
        400: {"description": "Ошибка валидации данных"},
        401: {"description": "Недействительный refresh токен"},
        404: {"description": "Пользователь не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def refresh_token(
    request: AdminRefreshRequest,
    session: AsyncSession = Depends(get_session),
) -> AdminRefreshResponse:
    """Обновление токена доступа.

    Требует валидный refresh token.
    Возвращает новый access token для продолжения работы.
    """
    return await admin_user_service.refresh_access_token(session, request.refresh_token)


@router.get(
    "/me",
    response_model=AdminMeResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение информации о текущем администраторе",
    description="Возвращает информацию о текущем авторизованном администраторе",
    responses={
        200: {"description": "Информация об администраторе успешно получена"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_current_admin_info(current_admin: ActiveAdmin) -> AdminMeResponse:
    """Получение информации о текущем администраторе.

    Требует авторизации с активным администратором.
    Возвращает основную информацию о текущем администраторе.
    """
    return admin_user_service.get_current_admin_info(current_admin)


@router.post(
    "/password-reset",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Запрос восстановления пароля",
    description="Отправляет письмо с инструкциями по восстановлению пароля на указанный email",
    responses={
        200: {"description": "Письмо отправлено (если email существует)"},
        400: {"description": "Ошибка валидации email"},
        500: {"description": "Ошибка отправки письма"},
    },
)
async def request_password_reset(
    request: AdminPasswordResetRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Запрос восстановления пароля."""
    return await admin_user_service.initialize_password_reset(session, request.email)


@router.post(
    "/password-reset-confirm",
    response_model=AdminPasswordResetSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Подтверждение восстановления пароля",
    description="Подтверждает смену пароля по токену из письма и возвращает новые токены",
    responses={
        200: {"description": "Пароль успешно изменен, возвращены новые токены"},
        400: {"description": "Ошибка валидации данных"},
        401: {"description": "Недействительный или истекший токен"},
        404: {"description": "Пользователь не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def confirm_password_reset(
    request: AdminPasswordResetConfirmRequest,
    session: AsyncSession = Depends(get_session),
) -> AdminPasswordResetSuccessResponse:
    """Подтверждение восстановления пароля."""
    return await admin_user_service.confirm_password_reset(session, request.token, request.new_password)
