"""Сервис для работы с пунктами меню."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import activity_crud, menu_crud, telegram_user_crud
from backend.models.enums import AccessLevel, ActivityType
from backend.schemas.public.menu import MenuContentResponse, MenuItemListResponse, MenuItemResponse
from backend.validators.menu_item import menu_item_validator


class MenuItemService:
    """Сервис для работы с пунктами меню."""

    def __init__(self):
        """Инициализация сервиса Menu Item."""

    async def get_menu_items(
        self,
        telegram_user_id: int,
        parent_id: Optional[int] = None,
        include_children: bool = False,
        max_depth: int = 1,
        db: AsyncSession = None,
    ) -> MenuItemListResponse:
        """Получение структуры меню для пользователя.

        Args:
            telegram_user_id: ID пользователя в Telegram
            parent_id: ID родительского пункта меню
            include_children: Включить дочерние элементы в ответ
            max_depth: Максимальная глубина загрузки (1 = только прямые дети, 2 = дети + внуки)
            db: Сессия базы данных

        Returns:
            Список пунктов меню
        """
        user = await telegram_user_crud.get_by_telegram_id(db, telegram_user_id)
        menu_item_validator.validate_user_exists(user)

        if parent_id is not None:
            parent_item = await menu_crud.get(db, parent_id)
            menu_item_validator.validate_parent_menu_item(parent_item)

        user_access_level = AccessLevel.PREMIUM if user.subscription_type == "premium" else AccessLevel.FREE

        if include_children:
            items = await menu_crud.get_by_parent_id_with_children(db, parent_id, True, user_access_level, max_depth)
        else:
            items = await menu_crud.get_by_parent_id(db, parent_id, True, user_access_level)

        items_data = [MenuItemResponse.model_validate(item) for item in items]

        return MenuItemListResponse(items=items_data)

    async def get_menu_item_content(
        self, menu_id: int, telegram_user_id: int, max_depth: int = 1, db: AsyncSession = None
    ) -> MenuContentResponse:
        """Получение контента конкретного пункта меню.

        Args:
            menu_id: ID пункта меню
            telegram_user_id: ID пользователя в Telegram
            max_depth: Максимальная глубина загрузки дочерних элементов
            db: Сессия базы данных

        Returns:
            Контент пункта меню
        """
        user = await telegram_user_crud.get_by_telegram_id(db, telegram_user_id)
        menu_item_validator.validate_user_exists(user)

        user_access_level = AccessLevel.PREMIUM if user.subscription_type == "premium" else AccessLevel.FREE

        menu_item = await menu_crud.get_with_content_and_children(db, menu_id, user_access_level, max_depth)
        menu_item_validator.validate_menu_item_exists(menu_item)
        menu_item_validator.validate_menu_item_active(menu_item)
        menu_item_validator.validate_access_level(user_access_level, menu_item.access_level)

        async with db.begin():
            await activity_crud.create_activity(
                db=db,
                telegram_user_id=user.id,
                menu_item_id=menu_id,
                activity_type=ActivityType.NAVIGATION,
            )
            await menu_crud.increment_view_count(db, menu_id)

        return MenuContentResponse.model_validate(menu_item)


menu_item_service = MenuItemService()
