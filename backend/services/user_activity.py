"""Сервис для работы с активностью пользователей."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import activity_crud, menu_crud, telegram_user_crud
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

        async with db.begin():
            activity = await activity_crud.create_activity(
                db=db,
                telegram_user_id=user.id,
                menu_item_id=request.menu_item_id,
                activity_type=request.activity_type,
                search_query=request.search_query,
            )

        return self._build_activity_response(activity)

    def _build_activity_response(self, activity) -> UserActivityResponse:
        """Формирование ответа записи активности.

        Args:
            activity: Объект активности из базы данных

        Returns:
            Ответ с данными активности
        """
        return UserActivityResponse(
            id=activity.id,
            telegram_user_id=activity.telegram_user_id,
            menu_item_id=activity.menu_item_id,
            activity_type=activity.activity_type,
            rating=activity.rating,
            search_query=activity.search_query,
        )


user_activity_service = UserActivityService()
