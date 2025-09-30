"""Сервис для работы с активностью пользователей."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import activity_crud, menu_crud, telegram_user_crud
from backend.models.enums import ActivityType
from backend.schemas.public.user_activity import UserActivityRequest, UserActivityResponse
from backend.validators.user_activity import user_activity_validator


class UserActivityService:
    """Сервис для работы с активностью пользователей."""

    def __init__(self):
        """Инициализация сервиса User Activity."""
        self._validator = user_activity_validator

    async def record_activity(self, request: UserActivityRequest, db: AsyncSession) -> UserActivityResponse:
        """Запись активности пользователя.

        Args:
            request: Данные активности пользователя
            db: Сессия базы данных

        Returns:
            Ответ с данными созданной активности
        """
        user = await telegram_user_crud.get_by_telegram_id(db, request.telegram_user_id)
        self._validator.validate_user_exists(user)

        menu_item = None
        if request.menu_item_id is not None:
            menu_item = await menu_crud.get(db, request.menu_item_id)
            self._validator.validate_menu_item_exists(menu_item)

        self._validator.validate_search_query(request.search_query)

        activity = await activity_crud.create_activity(
            db=db,
            telegram_user_id=user.id,
            menu_item_id=request.menu_item_id,
            activity_type=request.activity_type,
            search_query=request.search_query,
        )

        # Обновляем view_count для активности просмотра (пока что так)
        if request.activity_type == ActivityType.NAVIGATION and request.menu_item_id is not None:
            await menu_crud.increment_view_count(db, request.menu_item_id)

        return UserActivityResponse.model_validate(activity)


user_activity_service = UserActivityService()
