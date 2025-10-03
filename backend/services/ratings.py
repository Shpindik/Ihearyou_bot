"""Сервис для работы с оценками материалов."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.menu_item import menu_item_crud
from backend.crud.telegram_user import telegram_user_crud
from backend.crud.user_activity import user_activity_crud
from backend.models.enums import ActivityType
from backend.schemas.public.ratings import RatingRequest, RatingResponse
from backend.validators.menu_item import menu_item_validator
from backend.validators.user_activity import user_activity_validator


class RatingService:
    """Сервис для работы с оценками материалов."""

    def __init__(self):
        """Инициализация сервиса Rating."""
        self.menu_item_crud = menu_item_crud
        self.telegram_user_crud = telegram_user_crud
        self.user_activity_crud = user_activity_crud
        self.user_activity_validator = user_activity_validator
        self.menu_item_validator = menu_item_validator

    async def rate_material(self, request: RatingRequest, db: AsyncSession) -> RatingResponse:
        """Оценка полезности материала пользователем.

        Args:
            request: Данные для оценки материала
            db: Сессия базы данных

        Returns:
            Ответ с результатом оценки

        """
        user = await self.telegram_user_crud.get_by_telegram_id(db, request.telegram_user_id)
        self.user_activity_validator.validate_user_exists(user)

        menu_item = await self.menu_item_crud.get(db, request.menu_item_id)
        self.menu_item_validator.validate_menu_item_exists(menu_item)
        self.menu_item_validator.validate_menu_item_active(menu_item)

        # Проверяем, что оценка корректна
        self.user_activity_validator.validate_rating(request.rating, ActivityType.RATING)

        # Создаем активность оценки
        await self.user_activity_crud.create_activity(
            db=db,
            telegram_user_id=user.id,
            menu_item_id=request.menu_item_id,
            activity_type=ActivityType.RATING,
            rating=request.rating,
        )

        # Обновляем статистику оценок материала
        await self.menu_item_crud.update_rating_stats(db=db, menu_id=request.menu_item_id, rating=request.rating)

        return RatingResponse(success=True)


rating_service = RatingService()
