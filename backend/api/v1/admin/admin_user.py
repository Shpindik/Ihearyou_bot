"""Административные эндпоинты для управления пользователями администратора."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.core.dependencies import AdminOnly, ModeratorOrAdmin
from backend.schemas.admin.admin_user import (
    AdminUserCreate,
    AdminUserListResponse,
    AdminUserPasswordUpdate,
    AdminUserResponse,
    AdminUserUpdate,
)
from backend.services.admin_user import admin_user_service


router = APIRouter(prefix="/users", tags=["Admin Users"])


@router.get(
    "/",
    response_model=AdminUserListResponse,
    status_code=status.HTTP_200_OK,
    summary="Список администраторов",
    description="Получить список всех администраторов",
    responses={
        200: {"description": "Список администраторов успешно получен"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_admin_users(
    current_admin: AdminOnly,
    db: AsyncSession = Depends(get_session),
) -> AdminUserListResponse:
    """Получить список всех администраторов.

    Требует авторизации с ролью администратора.
    """
    return await admin_user_service.get_admin_users_for_api(session=db)


@router.get(
    "/{admin_id}",
    response_model=AdminUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение информации об администраторе",
    description="Получить детальную информацию об администраторе по ID",
    responses={
        200: {"description": "Информация об администраторе успешно получена"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Администратор не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_admin_user(
    admin_id: int,
    current_admin: AdminOnly,
    db: AsyncSession = Depends(get_session),
) -> AdminUserResponse:
    """Получить информацию об администраторе по ID.

    Требует авторизации с ролью администратора.
    """
    return await admin_user_service.get_admin_user_by_id(session=db, admin_id=admin_id)


@router.post(
    "/",
    response_model=AdminUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового администратора",
    description="Создает нового администратора в системе",
    responses={
        201: {"description": "Администратор успешно создан"},
        400: {"description": "Ошибка валидации данных (неверный формат email, слабый пароль и т.д.)"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа (требуется роль администратора)"},
        409: {"description": "Конфликт данных (email или username уже существует)"},
        422: {"description": "Ошибка валидации данных запроса"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def create_admin_user(
    admin_data: AdminUserCreate,
    current_admin: AdminOnly,
    db: AsyncSession = Depends(get_session),
) -> AdminUserResponse:
    """Создать нового администратора.

    Требует авторизации с ролью администратора.
    Создается администратор с указанными данными и автоматически хэшированным паролем.
    """
    return await admin_user_service.create_admin_for_api(session=db, admin_data=admin_data)


@router.patch(
    "/{admin_id}",
    response_model=AdminUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Частичное обновление администратора",
    description="Обновляет указанные поля администратора или изменяет его статус (активация/деактивация)",
    responses={
        200: {"description": "Администратор успешно обновлен"},
        400: {"description": "Ошибка валидации данных"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Администратор не найден"},
        409: {"description": "Конфликт данных (email или username уже существует)"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def update_admin_user(
    admin_id: int,
    admin_update: AdminUserUpdate,
    current_admin: AdminOnly,
    db: AsyncSession = Depends(get_session),
) -> AdminUserResponse:
    """Обновить данные администратора.

    Требует авторизации с ролью администратора.
    Обновляет только указанные поля.
    Поддерживает изменение статуса через поле is_active.
    """
    return await admin_user_service.update_admin_for_api(
        session=db,
        admin_id=admin_id,
        admin_update=admin_update,
    )


@router.patch(
    "/{admin_id}/password",
    response_model=AdminUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Изменение пароля администратора",
    description="Изменяет пароль администратора",
    responses={
        200: {"description": "Пароль успешно изменен"},
        400: {"description": "Ошибка валидации данных"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Администратор не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def update_admin_password(
    admin_id: int,
    password_data: AdminUserPasswordUpdate,
    current_admin: ModeratorOrAdmin,
    db: AsyncSession = Depends(get_session),
) -> AdminUserResponse:
    """Изменить пароль администратора.

    Требует авторизации с ролью модератора или администратора.
    Пароль хэшируется перед сохранением в базе данных.
    """
    return await admin_user_service.update_admin_password_for_api(
        session=db,
        admin_id=admin_id,
        password_data=password_data,
    )
