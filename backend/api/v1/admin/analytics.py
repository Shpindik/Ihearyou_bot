"""Административные эндпоинты для аналитики."""

from fastapi import APIRouter, Depends, Query, status
from fastapi.security import HTTPBearer

from backend.schemas.admin.analytics import AdminAnalyticsResponse


router = APIRouter(prefix="/admin/analytics", tags=["Admin Analytics"])
security = HTTPBearer()


@router.get("/", response_model=AdminAnalyticsResponse, status_code=status.HTTP_200_OK)
async def get_analytics(
    period: str = Query("month", description="Период (day, week, month, year)"),
    start_date: str = Query(None, description="Начальная дата (ISO 8601)"),
    end_date: str = Query(None, description="Конечная дата (ISO 8601)"),
    token: str = Depends(security),
) -> AdminAnalyticsResponse:
    """Получение базовой аналитики и статистики.

    GET /api/v1/admin/analytics
    Требует: Authorization: Bearer <token>
    Возвращает: статистику по пользователям, контенту, активностям и вопросам
    """
    pass
