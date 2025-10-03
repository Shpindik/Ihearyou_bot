"""Сервис для работы с аналитикой системы."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.analytics import analytics_crud
from backend.models.admin_user import AdminUser
from backend.schemas.admin.analytics import AdminAnalyticsRequest, AdminAnalyticsResponse
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
        request: AdminAnalyticsRequest,
    ) -> AdminAnalyticsResponse:
        """Получение комплексной аналитики системы по дням.

        Args:
            db: Сессия базы данных
            current_admin: Текущий администратор
            request: Валидированные данные запроса аналитики

        Returns:
            Полная аналитика системы

        """
        # Валидация доступа
        self.validator.validate_admin_access(current_admin)

        # Парсинг дат из предварительно валидированного запроса
        parsed_start_date, parsed_end_date = self.validator.parse_and_validate_dates(request.model_dump())

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
