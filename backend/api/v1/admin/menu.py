"""Административные эндпоинты для управления меню."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.core.dependencies import AdminOnly, ModeratorOrAdmin
from backend.models.enums import AccessLevel
from backend.schemas.admin.menu import (
    AdminContentFileCreate,
    AdminContentFileResponse,
    AdminContentFileUpdate,
    AdminMenuItemCreate,
    AdminMenuItemListResponse,
    AdminMenuItemResponse,
    AdminMenuItemUpdate,
)
from backend.services.content_file import content_file_service
from backend.services.menu_item import menu_item_service


router = APIRouter(prefix="/admin/menu-items", tags=["Admin Menu"])


@router.get(
    "/",
    response_model=AdminMenuItemListResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение списка пунктов меню (админ)",
    description="Возвращает список пунктов меню с возможностью фильтрации для администраторов",
    responses={
        200: {"description": "Список пунктов меню успешно получен"},
        400: {"description": "Ошибка валидации параметров запроса"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_admin_menu_items(
    current_admin: ModeratorOrAdmin,
    db: AsyncSession = Depends(get_session),
    parent_id: Optional[int] = Query(None, description="Фильтр по родительскому пункту"),
    is_active: Optional[bool] = Query(None, description="Фильтр по активности"),
    access_level: Optional[AccessLevel] = Query(None, description="Фильтр по уровню доступа (free, premium)"),
) -> AdminMenuItemListResponse:
    """Получение списка пунктов меню для администраторов.

    Требует авторизации с ролью модератора или администратора.
    Возвращает все пункты меню с возможностью фильтрации.
    """
    return await menu_item_service.get_admin_menu_items(
        db=db,
        parent_id=parent_id,
        is_active=is_active,
        access_level=access_level,
    )


@router.post(
    "/",
    response_model=AdminMenuItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового пункта меню (админ)",
    description="Создает новый пункт меню в системе",
    responses={
        201: {"description": "Пункт меню успешно создан"},
        400: {"description": "Ошибка валидации данных"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def create_menu_item(
    request: AdminMenuItemCreate, current_admin: ModeratorOrAdmin, db: AsyncSession = Depends(get_session)
) -> AdminMenuItemResponse:
    """Создание нового пункта меню.

    Требует авторизации с ролью модератора или администратора.
    Создает новый пункт меню с указанными параметрами.
    """
    return await menu_item_service.create_admin_menu_item(db=db, request=request)


@router.put(
    "/{id}",
    response_model=AdminMenuItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновление пункта меню (админ)",
    description="Обновляет существующий пункт меню",
    responses={
        200: {"description": "Пункт меню успешно обновлен"},
        400: {"description": "Ошибка валидации данных"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Пункт меню не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def update_menu_item(
    id: int, request: AdminMenuItemUpdate, current_admin: AdminOnly, db: AsyncSession = Depends(get_session)
) -> AdminMenuItemResponse:
    """Обновление пункта меню.

    Требует авторизации с ролью администратора.
    Обновляет существующий пункт меню с указанными параметрами.
    """
    return await menu_item_service.update_admin_menu_item(db=db, menu_id=id, request=request)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление пункта меню (админ)",
    description="Удаляет существующий пункт меню",
    responses={
        204: {"description": "Пункт меню успешно удален"},
        400: {"description": "Ошибка валидации данных"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Пункт меню не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def delete_menu_item(id: int, current_admin: AdminOnly, db: AsyncSession = Depends(get_session)) -> None:
    """Удаление пункта меню.

    Требует авторизации с ролью администратора.
    Удаляет существующий пункт меню (только если нет дочерних элементов).
    """
    await menu_item_service.delete_admin_menu_item(db=db, menu_id=id)


@router.get(
    "/{id}/content-files",
    response_model=list[AdminContentFileResponse],
    status_code=status.HTTP_200_OK,
    summary="Получение файлов контента (админ)",
    description="Возвращает список файлов контента для указанного пункта меню",
    responses={
        200: {"description": "Список файлов контента успешно получен"},
        400: {"description": "Ошибка валидации параметров запроса"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Пункт меню не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_content_files(
    id: int, current_admin: ModeratorOrAdmin, db: AsyncSession = Depends(get_session)
) -> list[AdminContentFileResponse]:
    """Получение файлов контента для пункта меню.

    Требует авторизации с ролью модератора или администратора.
    Возвращает все файлы контента, привязанные к указанному пункту меню.
    """
    return await content_file_service.get_content_files(db=db, menu_item_id=id)


@router.post(
    "/{id}/content-files",
    response_model=AdminContentFileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание файла контента (админ)",
    description="Создает новый файл контента для указанного пункта меню",
    responses={
        201: {"description": "Файл контента успешно создан"},
        400: {"description": "Ошибка валидации данных"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Пункт меню не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def create_content_file(
    id: int, request: AdminContentFileCreate, current_admin: AdminOnly, db: AsyncSession = Depends(get_session)
) -> AdminContentFileResponse:
    """Добавление файла контента к пункту меню.

    Требует авторизации с ролью администратора.
    Создает новый файл контента и привязывает его к указанному пункту меню.
    """
    return await content_file_service.create_content_file(db=db, menu_item_id=id, request=request)


@router.put(
    "/content-files/{file_id}",
    response_model=AdminContentFileResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновление файла контента (админ)",
    description="Обновляет существующий файл контента",
    responses={
        200: {"description": "Файл контента успешно обновлен"},
        400: {"description": "Ошибка валидации данных"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Файл контента не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def update_content_file(
    file_id: int, request: AdminContentFileUpdate, current_admin: AdminOnly, db: AsyncSession = Depends(get_session)
) -> AdminContentFileResponse:
    """Обновление файла контента.

    Требует авторизации с ролью администратора.
    Обновляет существующий файл контента с указанными параметрами.
    """
    return await content_file_service.update_content_file(db=db, file_id=file_id, request=request)


@router.delete(
    "/content-files/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление файла контента (админ)",
    description="Удаляет существующий файл контента",
    responses={
        204: {"description": "Файл контента успешно удален"},
        400: {"description": "Ошибка валидации данных"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Файл контента не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def delete_content_file(file_id: int, current_admin: AdminOnly, db: AsyncSession = Depends(get_session)) -> None:
    """Удаление файла контента.

    Требует авторизации с ролью администратора.
    Удаляет существующий файл контента из системы.
    """
    await content_file_service.delete_content_file(db=db, file_id=file_id)
