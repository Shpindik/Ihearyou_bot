"""Публичные эндпоинты для поиска по материалам."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.core.exceptions import ValidationError
from backend.schemas.public.search import SearchListResponse
from backend.services.menu_item import menu_item_service


router = APIRouter(prefix="/search", tags=["Public Search"])


@router.get("/", response_model=SearchListResponse, status_code=status.HTTP_200_OK)
async def search_materials(
    telegram_user_id: int = Query(..., description="ID пользователя в Telegram"),
    query: str = Query(..., description="Поисковый запрос"),
    limit: int = Query(10, description="Лимит результатов (по умолчанию 10)"),
    db: AsyncSession = Depends(get_session),
) -> SearchListResponse:
    """Поиск по материалам.

    GET /api/v1/search
    Параметры:
    - telegram_user_id (int, обязательный) - ID пользователя в Telegram
    - query (string, обязательный) - Поисковый запрос
    - limit (int, необязательный) - Лимит результатов (по умолчанию 10)
    """
    try:
        return await menu_item_service.search_menu_items(
            telegram_user_id=telegram_user_id,
            query=query,
            limit=limit,
            db=db,
        )
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Ошибка при выполнении поиска: {str(e)}")
