"""Публичные эндпоинты для поиска по материалам."""

from fastapi import APIRouter, Query, status

from schemas.public.search import (
    SearchListResponse,
)

router = APIRouter(prefix="/search", tags=["Public Search"])


@router.get("/", response_model=SearchListResponse, status_code=status.HTTP_200_OK)
async def search_materials(
    telegram_user_id: int = Query(..., description="ID пользователя в Telegram"),
    query: str = Query(..., description="Поисковый запрос"),
    limit: int = Query(10, description="Лимит результатов (по умолчанию 10)")
) -> SearchListResponse:
    """
    Поиск по материалам.
    
    GET /api/v1/search
    Параметры:
    - telegram_user_id (int, обязательный) - ID пользователя в Telegram
    - query (string, обязательный) - Поисковый запрос
    - limit (int, необязательный) - Лимит результатов (по умолчанию 10)
    """
    pass
