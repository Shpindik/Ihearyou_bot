"""Сервис для работы с активностью пользователей."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.menu_item import menu_item_crud
from backend.crud.telegram_user import telegram_user_crud
from backend.crud.user_activity import user_activity_crud
from backend.models.enums import AccessLevel, ActivityType
from backend.schemas.public.user_activity import UserActivityRequest, UserActivityResponse
from backend.services.telegram_user import telegram_user_service
from backend.validators.menu_item import menu_item_validator
from backend.validators.telegram_user import telegram_user_validator
from backend.validators.user_activity import user_activity_validator


class UserActivityService:
    """Сервис для работы с активностью пользователей."""

    def __init__(self):
        """Инициализация сервиса User Activity."""
        self.user_activity_crud = user_activity_crud
        self.menu_item_crud = menu_item_crud
        self.telegram_user_crud = telegram_user_crud
        self.user_activity_validator = user_activity_validator
        self.menu_item_validator = menu_item_validator

    async def record_activity(self, request: UserActivityRequest, db: AsyncSession) -> UserActivityResponse:
        """Запись активности пользователя.

        Args:
            request: Данные активности пользователя
            db: Сессия базы данных

        Returns:
            Ответ с данными созданной активности
        """
        user = await self.telegram_user_crud.get_by_telegram_id(db, request.telegram_user_id)
        telegram_user_validator.validate_user_exists(user)

        menu_item = None
        if request.menu_item_id is not None:
            menu_item = await self.menu_item_crud.get(db, request.menu_item_id)
            self.menu_item_validator.validate_menu_item_exists(menu_item)

            user_access_level = (
                AccessLevel.PREMIUM if getattr(user, "subscription_type", None) == "premium" else AccessLevel.FREE
            )
            self.menu_item_validator.validate_access_level(user_access_level, menu_item.access_level)

        self.user_activity_validator.validate_search_query(request.search_query)

        activity = await self.user_activity_crud.create_activity(
            db=db,
            telegram_user_id=user.id,
            menu_item_id=request.menu_item_id,
            activity_type=request.activity_type,
            search_query=request.search_query,
        )

        # Обновляем статистику материала в зависимости от типа активности
        if request.menu_item_id is not None:
            if request.activity_type in [
                ActivityType.NAVIGATION,
                ActivityType.TEXT_VIEW,
                ActivityType.IMAGE_VIEW,
                ActivityType.VIDEO_VIEW,
                ActivityType.MATERIAL_OPEN,
                ActivityType.SECTION_ENTER,
            ]:
                await self.menu_item_crud.increment_view_count(db=db, menu_id=request.menu_item_id)
            elif request.activity_type in [ActivityType.PDF_DOWNLOAD, ActivityType.MEDIA_VIEW]:
                await self.menu_item_crud.increment_download_count(db=db, menu_id=request.menu_item_id)
            elif request.activity_type == ActivityType.RATING:
                await self.menu_item_crud.update_rating_stats(
                    db=db, menu_id=request.menu_item_id, rating=request.rating
                )

        # Обновляем счетчик активностей пользователя через сервис
        await telegram_user_service.increment_user_activities_count(db=db, telegram_user_id=user.id)

        return UserActivityResponse(
            menu_item_id=activity.menu_item_id,
            activity_type=activity.activity_type,
            rating=activity.rating,
            search_query=activity.search_query,
            message="Активность успешно записана",
        )


user_activity_service = UserActivityService()
