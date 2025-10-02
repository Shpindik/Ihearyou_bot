"""Публичные эндпоинты для поиска по материалам."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.schemas.public.search import SearchListResponse
from backend.services.menu_item import menu_item_service


router = APIRouter(prefix="/search", tags=["Public Search"])


@router.get(
    "/",
    response_model=SearchListResponse,
    status_code=status.HTTP_200_OK,
    summary="Поиск по материалам системы",
    description="Возвращает список пунктов меню соответствующих поисковому запросу с учетом уровня доступа пользователя",
    responses={
        200: {"description": "Результаты поиска успешно получены"},
        400: {"description": "Ошибка валидации параметров запроса"},
        404: {"description": "Пользователь не найден"},
        422: {"description": "Поисковый запрос содержит недопустимые символы или слишком много повторяющихся символов"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def search_materials(
    telegram_user_id: int = Query(..., description="ID пользователя в Telegram", gt=0),
    query: str = Query(..., description="Поисковый запрос", min_length=2, max_length=100),
    limit: int = Query(10, description="Лимит результатов (по умолчанию 10)", gt=0, le=100),
    db: AsyncSession = Depends(get_session),
) -> SearchListResponse:
    """Поиск по материалам системы.

    Выполняет поиск по названию и описанию пунктов меню с учетом уровня доступа пользователя.
    Требует наличия пользователя в системе (регистрация через Bot API).
    """
    return await menu_item_service.search_menu_items(
        telegram_user_id=telegram_user_id,
        query=query,
        limit=limit,
        db=db,
    )
