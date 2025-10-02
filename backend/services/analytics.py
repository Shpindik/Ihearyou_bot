"""Сервис для работы с аналитикой системы."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.analytics import analytics_crud
from backend.models.admin_user import AdminUser
from backend.schemas.admin.analytics import AdminAnalyticsResponse
from backend.validators.analytics import analytics_validator


class AnalyticsService:
    """Сервис для работы с аналитикой системы."""

    def __init__(self):
        """Инициализация сервиса Analytics."""
        self.analytics_crud = analytics_crud
        self.validator = analytics_validator

    async def get_analytics(
        self,
        db: AsyncSession,
        current_admin: AdminUser,
        period: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> AdminAnalyticsResponse:
        """Получение комплексной аналитики системы.

        Args:
            db: Сессия базы данных
            current_admin: Текущий администратор
            period: Период аналитики (day, week, month, year)
            start_date: Начальная дата в формате ISO 8601
            end_date: Конечная дата в формате ISO 8601

        Returns:
            Полная аналитика системы

        """
        # Валидация доступа
        self.validator.validate_admin_access(current_admin)

        # Валидация параметров
        if period:
            self.validator.validate_period(period)

        # Парсинг дат
        date_range = self.validator.validate_date_range(start_date, end_date, period)
        parsed_start_date, parsed_end_date = date_range if date_range else (None, None)

        # Если передан период, то вычисляем диапазон дат
        if period and not parsed_start_date:
            parsed_end_date = datetime.now()
            if period == "day":
                parsed_start_date = parsed_end_date - timedelta(days=1)
            elif period == "week":
                parsed_start_date = parsed_end_date - timedelta(weeks=1)
            elif period == "month":
                parsed_start_date = parsed_end_date - timedelta(days=30)
            elif period == "year":
                parsed_start_date = parsed_end_date - timedelta(days=365)

        # Получение статистики пользователей
        users_stats = await self.analytics_crud.get_users_statistics(
            db=db, start_date=parsed_start_date, end_date=parsed_end_date
        )

        # Получение статистики контента
        content_stats = await self.analytics_crud.get_content_statistics(
            db=db, start_date=parsed_start_date, end_date=parsed_end_date
        )

        # Получение статистики активностей
        activities_stats = await self.analytics_crud.get_activities_statistics(
            db=db, start_date=parsed_start_date, end_date=parsed_end_date
        )

        # Получение статистики вопросов
        questions_stats = await self.analytics_crud.get_questions_statistics(
            db=db, start_date=parsed_start_date, end_date=parsed_end_date
        )

        return AdminAnalyticsResponse(
            users=users_stats,
            content=content_stats,
            activities=activities_stats,
            questions=questions_stats,
        )


analytics_service = AnalyticsService()
