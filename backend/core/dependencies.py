"""Зависимости для FastAPI эндпойнтов."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.models.admin_user import AdminUser
from backend.models.enums import AdminRole
from backend.services.admin_user import admin_user_service
from backend.validators.admin_user import admin_user_validator


security = HTTPBearer()


async def get_current_admin(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AdminUser:
    """Получение текущего администратора по JWT токену.

    Args:
        credentials: Bearer токен из заголовка Authorization
        session: Сессия базы данных

    Returns:
        AdminUser: Текущий администратор

    Raises:
        HTTPException: 401 если токен недействителен или пользователь не найден
    """
    token = credentials.credentials
    return await admin_user_service.authenticate_admin_by_token(session, token)


async def get_current_active_admin(
    current_admin: Annotated[AdminUser, Depends(get_current_admin)],
) -> AdminUser:
    """Получение активного администратора.

    Args:
        current_admin: Текущий администратор

    Returns:
        AdminUser: Активный администратор

    Raises:
        HTTPException: 401 если пользователь неактивен
    """
    return admin_user_validator.validate_admin_active(current_admin)


def require_admin_role(
    current_admin: Annotated[AdminUser, Depends(get_current_active_admin)],
) -> AdminUser:
    """Требует роль администратора.

    Args:
        current_admin: Текущий активный администратор

    Returns:
        AdminUser: Администратор с ролью admin

    Raises:
        HTTPException: 403 если недостаточно прав
    """
    return admin_user_validator.validate_admin_role(current_admin, AdminRole.ADMIN)


def require_moderator_or_admin_role(
    current_admin: Annotated[AdminUser, Depends(get_current_active_admin)],
) -> AdminUser:
    """Требует роль модератора или администратора.

    Args:
        current_admin: Текущий активный администратор

    Returns:
        AdminUser: Администратор с ролью moderator или admin

    Raises:
        HTTPException: 403 если недостаточно прав
    """
    return admin_user_validator.validate_admin_roles(current_admin, [AdminRole.MODERATOR, AdminRole.ADMIN])


# Типы для аннотаций
Admin = Annotated[AdminUser, Depends(get_current_active_admin)]
AdminOnly = Annotated[AdminUser, Depends(require_admin_role)]
ModeratorOrAdmin = Annotated[AdminUser, Depends(require_moderator_or_admin_role)]
