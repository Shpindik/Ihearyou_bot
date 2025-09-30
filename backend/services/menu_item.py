"""Сервис для работы с пунктами меню."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import menu_crud, telegram_user_crud, activity_crud
from backend.models.enums import AccessLevel, ActivityType
from backend.schemas.public.menu import MenuContentResponse, MenuItemListResponse, MenuItemResponse
from backend.schemas.public.search import SearchItemResponse, SearchListResponse
from backend.validators.menu_item import menu_item_validator


class MenuItemService:
    """Сервис для работы с пунктами меню."""

    def __init__(self):
        """Инициализация сервиса Menu Item."""

    async def get_menu_items(
        self,
        telegram_user_id: int,
        parent_id: Optional[int] = None,
        db: AsyncSession = None,
    ) -> MenuItemListResponse:
        """Получение пунктов меню для пользователя (только один уровень).

        Args:
            telegram_user_id: ID пользователя в Telegram
            parent_id: ID родительского пункта меню (None для корневого уровня)
            db: Сессия базы данных

        Returns:
            Список пунктов меню одного уровня
        """
        user = await telegram_user_crud.get_by_telegram_id(db, telegram_user_id)
        menu_item_validator.validate_user_exists(user)

        if parent_id is not None:
            parent_item = await menu_crud.get(db, parent_id)
            menu_item_validator.validate_parent_menu_item(parent_item)

        user_access_level = (
            AccessLevel.PREMIUM if getattr(user, "subscription_type", None) == "premium" else AccessLevel.FREE
        )

        # Загружаем только один уровень
        items = await menu_crud.get_by_parent_id(db, parent_id, True, user_access_level)

        # Простая сериализация без рекурсии
        items_data = [
            MenuItemResponse(
                id=item.id,
                title=item.title,
                description=item.description,
                parent_id=item.parent_id,
                bot_message=item.bot_message,
                is_active=item.is_active,
                access_level=item.access_level,
                children=[],  # Всегда пустой список для MVP
            )
            for item in items
        ]

        return MenuItemListResponse(items=items_data)

    async def get_menu_item_content(
        self, menu_id: int, telegram_user_id: int, db: AsyncSession = None
    ) -> MenuContentResponse:
        """Получение контента конкретного пункта меню с прямыми дочерними элементами.

        Args:
            menu_id: ID пункта меню
            telegram_user_id: ID пользователя в Telegram
            db: Сессия базы данных

        Returns:
            Контент пункта меню с дочерними элементами
        """
        user = await telegram_user_crud.get_by_telegram_id(db, telegram_user_id)
        menu_item_validator.validate_user_exists(user)

        user_access_level = (
            AccessLevel.PREMIUM if getattr(user, "subscription_type", None) == "premium" else AccessLevel.FREE
        )

        menu_item = await menu_crud.get_with_content_and_children(db, menu_id, user_access_level)
        menu_item_validator.validate_menu_item_exists(menu_item)
        menu_item_validator.validate_menu_item_active(menu_item)
        menu_item_validator.validate_access_level(user_access_level, menu_item.access_level)

        # Простая сериализация дочерних элементов
        children = [
            MenuItemResponse(
                id=child.id,
                title=child.title,
                description=child.description,
                parent_id=child.parent_id,
                bot_message=child.bot_message,
                is_active=child.is_active,
                access_level=child.access_level,
                children=[],  # Всегда пустой список для MVP
            )
            for child in getattr(menu_item, "_children", [])
        ]

        # Создаем ответ с использованием Pydantic
        return MenuContentResponse(
            id=menu_item.id,
            title=menu_item.title,
            description=menu_item.description,
            bot_message=menu_item.bot_message,
            content_files=menu_item.content_files,
            children=children,
        )

    async def search_menu_items(
        self,
        telegram_user_id: int,
        query: str,
        limit: int,
        db: AsyncSession,
    ) -> SearchListResponse:
        """Поиск по материалам (пунктам меню).

        Args:
            telegram_user_id: ID пользователя в Telegram
            query: Поисковый запрос (будет валидирован)
            limit: Максимальное количество результатов
            db: Сессия базы данных

        Returns:
            SearchListResponse: Список найденных пунктов меню

        Raises:
            ValidationError: Если пользователь не найден или запрос некорректен
        """
        user = await telegram_user_crud.get_by_telegram_id(db, telegram_user_id)
        menu_item_validator.validate_user_exists(user)

        normalized_query = menu_item_validator.validate_search_query(query)

        user_access_level = (
            AccessLevel.PREMIUM
            if getattr(user, "subscription_type", None) == "premium"
            else AccessLevel.FREE
        )

        items = await menu_crud.search_by_query(
            db=db,
            query=normalized_query,
            access_level=user_access_level,
            limit=limit,
        )

        try:
            await activity_crud.create(
                db=db,
                obj_in={
                    "telegram_user_id": telegram_user_id,
                    "menu_item_id": None,
                    "activity_type": ActivityType.SEARCH,
                    "search_query": {"query": normalized_query, "results_count": len(items)},
                }
            )
            await db.commit()
        except Exception as e:
            await db.rollback()

        items_data = [
            SearchItemResponse(
                id=item.id,
                title=item.title,
                description=item.description,
                parent_id=item.parent_id,
                bot_message=item.bot_message,
                is_active=item.is_active,
                access_level=item.access_level,
            )
            for item in items
        ]

        return SearchListResponse(items=items_data)


menu_item_service = MenuItemService()
