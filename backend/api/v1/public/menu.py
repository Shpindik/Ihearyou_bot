"""Публичные эндпоинты для работы с меню."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.schemas.public.menu import MenuContentResponse, MenuItemListResponse
from backend.services.menu_item import menu_item_service


router = APIRouter(prefix="/menu-items")


@router.get(
    "/",
    response_model=MenuItemListResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение структуры меню",
    description="Возвращает структуру меню для пользователя с возможностью фильтрации по родительскому элементу",
    responses={
        200: {"description": "Структура меню успешно получена"},
        400: {"description": "Ошибка валидации параметров запроса"},
        404: {"description": "Пользователь не найден или родительский пункт меню не найден"},
        422: {"description": "Ошибка валидации входных данных"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_menu_items(
    telegram_user_id: int = Query(..., description="ID пользователя в Telegram", gt=0),
    parent_id: Optional[int] = Query(None, description="ID родительского пункта меню (null для корневого уровня)"),
    db: AsyncSession = Depends(get_session),
) -> MenuItemListResponse:
    """Получение пунктов меню для пользователя (один уровень).

    Пользователь должен быть зарегистрирован через Bot API.
    Возвращает только один уровень меню для простоты MVP.
    """
    return await menu_item_service.get_menu_items(telegram_user_id=telegram_user_id, parent_id=parent_id, db=db)


@router.get(
    "/{id}/content",
    response_model=MenuContentResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение контента пункта меню",
    description="Возвращает полный контент конкретного пункта меню включая файлы и дочерние элементы",
    responses={
        200: {"description": "Контент пункта меню успешно получен"},
        400: {"description": "Ошибка валидации параметров запроса"},
        403: {"description": "Недостаточно прав для доступа к контенту"},
        404: {"description": "Пользователь не найден или пункт меню не найден"},
        422: {"description": "Ошибка валидации входных данных"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_menu_item_content(
    id: int,
    telegram_user_id: int = Query(..., description="ID пользователя в Telegram", gt=0),
    db: AsyncSession = Depends(get_session),
) -> MenuContentResponse:
    """Получение контента конкретного пункта меню с дочерними элементами.

    Проверяет права доступа пользователя к контенту.
    Возвращает контент и прямых дочерних элементов.
    """
    return await menu_item_service.get_menu_item_content(menu_id=id, telegram_user_id=telegram_user_id, db=db)
