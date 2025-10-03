"""Сервис для работы с пунктами меню."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.menu_item import menu_item_crud
from backend.crud.telegram_user import telegram_user_crud
from backend.crud.user_activity import user_activity_crud
from backend.models.enums import AccessLevel, ActivityType, ItemType
from backend.schemas.admin.menu import (
    AdminMenuItemCreate,
    AdminMenuItemListResponse,
    AdminMenuItemResponse,
    AdminMenuItemUpdate,
)
from backend.schemas.public.menu import ContentFileResponse, MenuContentResponse, MenuItemListResponse, MenuItemResponse
from backend.schemas.public.search import SearchItemResponse, SearchListResponse
from backend.schemas.public.user_activity import UserActivityRequest
from backend.validators.menu_item import menu_item_validator


class MenuItemService:
    """Сервис для работы с пунктами меню."""

    def __init__(self):
        """Инициализация сервиса Menu Item."""
        self.menu_crud = menu_item_crud
        self.telegram_user_crud = telegram_user_crud
        self.validator = menu_item_validator

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
        user = await self.telegram_user_crud.get_by_telegram_id(db, telegram_user_id)
        self.validator.validate_user_exists(user)

        if parent_id is not None:
            parent_item = await self.menu_crud.get(db, parent_id)
            self.validator.validate_parent_menu_item(parent_item)

        user_access_level = (
            AccessLevel.PREMIUM if getattr(user, "subscription_type", None) == "premium" else AccessLevel.FREE
        )

        # Загружаем только один уровень
        items = await self.menu_crud.get_by_parent_id(db, parent_id, True, user_access_level)

        items_data = [
            MenuItemResponse(
                id=item.id,
                title=item.title,
                description=item.description,
                parent_id=item.parent_id,
                bot_message=item.bot_message,
                is_active=item.is_active,
                access_level=item.access_level,
                item_type=item.item_type,
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
        user = await self.telegram_user_crud.get_by_telegram_id(db, telegram_user_id)
        self.validator.validate_user_exists(user)

        user_access_level = (
            AccessLevel.PREMIUM if getattr(user, "subscription_type", None) == "premium" else AccessLevel.FREE
        )

        menu_item = await self.menu_crud.get_with_content_and_children(db, menu_id, user_access_level)
        self.validator.validate_menu_item_exists(menu_item)
        self.validator.validate_menu_item_active(menu_item)
        self.validator.validate_access_level(user_access_level, menu_item.access_level)

        # Проверяем логику типа кнопки
        if menu_item.item_type == ItemType.NAVIGATION and not getattr(menu_item, "_children", []):
            # Навигационная кнопка без дочерних элементов - возвращаем пустой контент
            return MenuContentResponse(
                id=menu_item.id,
                title=menu_item.title,
                description=menu_item.description,
                bot_message="Раздел пока пуст. Попробуйте позже.",
                item_type=menu_item.item_type,
                content_files=[],
                children=[],
            )

        children = [
            MenuItemResponse(
                id=child.id,
                title=child.title,
                description=child.description,
                parent_id=child.parent_id,
                bot_message=child.bot_message,
                is_active=child.is_active,
                access_level=child.access_level,
                item_type=child.item_type,
                children=[],  # Всегда пустой список для MVP
            )
            for child in getattr(menu_item, "_children", [])
        ]

        # Формируем content_files в правильном формате
        content_files = []
        if menu_item.content:
            content_files = [
                ContentFileResponse(
                    content_type=menu_item.content.content_type,
                    caption=menu_item.content.caption,
                    text_content=menu_item.content.text_content,
                    external_url=menu_item.content.external_url,
                    web_app_short_name=menu_item.content.web_app_short_name,
                    telegram_file_id=menu_item.content.telegram_file_id,
                    file_size=menu_item.content.file_size,
                    mime_type=menu_item.content.mime_type,
                    width=menu_item.content.width,
                    height=menu_item.content.height,
                    duration=menu_item.content.duration,
                    thumbnail_telegram_file_id=menu_item.content.thumbnail_telegram_file_id,
                )
            ]

        return MenuContentResponse(
            id=menu_item.id,
            title=menu_item.title,
            description=menu_item.description,
            bot_message=menu_item.bot_message,
            item_type=menu_item.item_type,
            content_files=content_files,
            children=children,
        )

    async def get_admin_menu_items(
        self,
        db: AsyncSession,
        parent_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        access_level: Optional[AccessLevel] = None,
    ) -> AdminMenuItemListResponse:
        """Получение пунктов меню для администраторов.

        Args:
            db: Сессия базы данных
            parent_id: ID родительского пункта меню
            is_active: Фильтр по активности
            access_level: Фильтр по уровню доступа

        Returns:
            Полный список пунктов меню для админки с метаданными
        """
        items = await self.menu_crud.get_admin_menu_items(db, parent_id, is_active, access_level)

        items_data = [
            AdminMenuItemResponse(
                id=item.id,
                title=item.title,
                description=item.description,
                parent_id=item.parent_id,
                bot_message=item.bot_message,
                is_active=item.is_active,
                access_level=item.access_level,
                item_type=item.item_type,
                view_count=item.view_count,
                download_count=item.download_count,
                rating_sum=item.rating_sum,
                rating_count=item.rating_count,
                average_rating=float(item.average_rating) if item.average_rating else None,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in items
        ]

        return AdminMenuItemListResponse(
            items=items_data,
            total=len(items_data),
            page=1,
            limit=len(items_data),
            pages=1,
        )

    async def create_admin_menu_item(self, db: AsyncSession, request: AdminMenuItemCreate) -> AdminMenuItemResponse:
        """Создание нового пункта меню (админ).

        Args:
            db: Сессия базы данных
            request: Данные для создания пункта меню

        Returns:
            Созданный пункт меню
        """
        if request.parent_id:
            parent_item = await self.menu_crud.get(db, request.parent_id)
            self.validator.validate_parent_menu_item(parent_item)

        menu_item = await self.menu_crud.create(db, obj_in=request)

        return AdminMenuItemResponse(
            id=menu_item.id,
            title=menu_item.title,
            description=menu_item.description,
            parent_id=menu_item.parent_id,
            bot_message=menu_item.bot_message,
            is_active=menu_item.is_active,
            access_level=menu_item.access_level,
            item_type=menu_item.item_type,
            view_count=menu_item.view_count,
            download_count=menu_item.download_count,
            rating_sum=menu_item.rating_sum,
            rating_count=menu_item.rating_count,
            average_rating=float(menu_item.average_rating) if menu_item.average_rating else None,
            created_at=menu_item.created_at,
            updated_at=menu_item.updated_at,
        )

    async def update_admin_menu_item(
        self, db: AsyncSession, menu_id: int, request: AdminMenuItemUpdate
    ) -> AdminMenuItemResponse:
        """Обновление пункта меню (админ).

        Args:
            db: Сессия базы данных
            menu_id: ID пункта меню
            request: Данные для обновления

        Returns:
            Обновленный пункт меню
        """
        menu_item = await self.menu_crud.get(db, menu_id)
        self.validator.validate_menu_item_exists(menu_item)

        if request.parent_id is not None:
            if request.parent_id == menu_id:
                self.validator.validate_menu_item_not_self_parent(menu_id)
            if request.parent_id:
                parent_item = await self.menu_crud.get(db, request.parent_id)
                self.validator.validate_parent_menu_item(parent_item)

        updated_item = await self.menu_crud.update(db, db_obj=menu_item, obj_in=request)

        return AdminMenuItemResponse(
            id=updated_item.id,
            title=updated_item.title,
            description=updated_item.description,
            parent_id=updated_item.parent_id,
            bot_message=updated_item.bot_message,
            is_active=updated_item.is_active,
            access_level=updated_item.access_level,
            item_type=updated_item.item_type,
            view_count=updated_item.view_count,
            download_count=updated_item.download_count,
            rating_sum=updated_item.rating_sum,
            rating_count=updated_item.rating_count,
            average_rating=float(updated_item.average_rating) if updated_item.average_rating else None,
            created_at=updated_item.created_at,
            updated_at=updated_item.updated_at,
        )

    async def delete_admin_menu_item(self, db: AsyncSession, menu_id: int) -> None:
        """Удаление пункта меню (админ).

        Args:
            db: Сессия базы данных
            menu_id: ID пункта меню
        """
        menu_item = await self.menu_crud.get(db, menu_id)
        self.validator.validate_menu_item_exists(menu_item)

        children = await self.menu_crud.get_children_by_parent_id(db, menu_id)
        self.validator.validate_menu_item_no_children(children)

        await self.menu_crud.remove(db, id=menu_id)

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
            AccessLevel.PREMIUM if getattr(user, "subscription_type", None) == "premium" else AccessLevel.FREE
        )

        items = await menu_item_crud.search_by_query(
            db=db,
            query=normalized_query,
            access_level=user_access_level,
            limit=limit,
        )

        items_data = [
            SearchItemResponse(
                id=item.id,
                title=item.title,
                description=item.description,
                parent_id=item.parent_id,
                bot_message=item.bot_message,
                is_active=item.is_active,
                access_level=item.access_level,
                item_type=item.item_type,
            )
            for item in items
        ]

        # Записываем активность поиска пользователя
        search_activity = UserActivityRequest(
            telegram_user_id=user.id,
            menu_item_id=None,
            activity_type=ActivityType.SEARCH,
            search_query=f"Поиск: '{normalized_query}' (результатов: {len(items)})",
        )
        await user_activity_crud.create(db=db, obj_in=search_activity)

        return SearchListResponse(items=items_data)


menu_item_service = MenuItemService()
