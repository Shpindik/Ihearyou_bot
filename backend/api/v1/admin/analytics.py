"""Административные эндпоинты для аналитики."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.core.dependencies import ModeratorOrAdmin
from backend.schemas.admin.analytics import AdminAnalyticsRequest, AdminAnalyticsResponse
from backend.services.analytics import analytics_service


router = APIRouter(prefix="/analytics", tags=["Admin Analytics"])


@router.get(
    "/",
    response_model=AdminAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение комплексной аналитики системы",
    description="Возвращает комплексную статистику по всем модулям системы с возможностью фильтрации по периодам и диапазонам дат",
    responses={
        200: {"description": "Аналитика успешно получена"},
        400: {"description": "Ошибка валидации параметров запроса или некорректный формат даты (YYYY-MM-DD)"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_analytics(
    current_admin: ModeratorOrAdmin,
    period: Optional[str] = Query("month", description="Период аналитики (day, week, month, year)"),
    start_date: Optional[str] = Query(None, description="Начальная дата фильтрации (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Конечная дата фильтрации (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_session),
) -> AdminAnalyticsResponse:
    """Получение комплексной аналитики и статистики системы по дням.

    Возвращает статистику по пользователям, контенту, активностям и вопросам.
    Поддерживает фильтрацию по периодам и диапазонам дат в формате YYYY-MM-DD.
    Аналитика предоставляется с разбивкой по дням как минимальной единице времени.
    """
    return await analytics_service.get_analytics(
        db=db,
        current_admin=current_admin,
        request=AdminAnalyticsRequest(
            start_date=start_date,
            end_date=end_date,
        ),
    )
