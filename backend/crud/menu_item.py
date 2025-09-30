"""CRUD операции для пунктов меню."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models import MenuItem
from backend.models.enums import AccessLevel

from .base import BaseCRUD


class MenuItemCRUD(BaseCRUD[MenuItem, dict, dict]):
    """CRUD операции для пунктов меню."""

    def __init__(self):
        """Инициализация CRUD для пунктов меню."""
        super().__init__(MenuItem)

    async def get_by_parent_id(
        self,
        db: AsyncSession,
        parent_id: Optional[int] = None,
        is_active: bool = True,
        access_level: Optional[AccessLevel] = None,
    ) -> List[MenuItem]:
        """Получить дочерние пункты меню."""
        query = select(MenuItem).where(MenuItem.parent_id == parent_id)

        if is_active:
            query = query.where(MenuItem.is_active)

        if access_level is not None:
            if access_level == AccessLevel.FREE:
                query = query.where(MenuItem.access_level == AccessLevel.FREE)

        query = query.order_by(MenuItem.id)

        result = await db.execute(query)
        items = result.scalars().all()

        return items

    async def get_by_parent_id_with_children(
        self,
        db: AsyncSession,
        parent_id: Optional[int] = None,
        is_active: bool = True,
        access_level: Optional[AccessLevel] = None,
        max_depth: int = 1,
    ) -> List[MenuItem]:
        """Получить дочерние пункты меню с их детьми с настраиваемой глубиной.

        Args:
            db: Сессия базы данных
            parent_id: ID родительского элемента (None для корневого уровня)
            is_active: Фильтр по активности
            access_level: Уровень доступа пользователя
            max_depth: Максимальная глубина загрузки
        """
        from sqlalchemy.orm import selectinload

        query = select(MenuItem).options(selectinload(MenuItem.children)).where(MenuItem.parent_id == parent_id)

        if is_active:
            query = query.where(MenuItem.is_active)

        if access_level is not None:
            if access_level == AccessLevel.FREE:
                query = query.where(MenuItem.access_level == AccessLevel.FREE)

        query = query.order_by(MenuItem.id)

        result = await db.execute(query)
        items = result.scalars().all()

        # Применяем фильтрацию и ограничение глубины к каждому элементу
        for item in items:
            self._filter_and_limit_depth(item, access_level or AccessLevel.FREE, max_depth, current_depth=0)

        return items

    async def get_with_content(self, db: AsyncSession, menu_id: int) -> Optional[MenuItem]:
        """Получить пункт меню с контентом."""
        query = select(MenuItem).options(selectinload(MenuItem.content_files)).where(MenuItem.id == menu_id)

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_with_content_and_children(
        self, db: AsyncSession, menu_id: int, access_level: AccessLevel, max_depth: int = 1
    ) -> Optional[MenuItem]:
        """Получить пункт меню с контентом и дочерними элементами с настраиваемой глубиной.

        Args:
            db: Сессия базы данных
            menu_id: ID пункта меню
            access_level: Уровень доступа пользователя
            max_depth: Максимальная глубина загрузки (1 = только прямые дети, 2 = дети + внуки, и т.д.)
        """
        query = (
            select(MenuItem)
            .options(selectinload(MenuItem.content_files), selectinload(MenuItem.children))
            .where(MenuItem.id == menu_id, MenuItem.is_active)
        )

        result = await db.execute(query)
        menu_item = result.scalar_one_or_none()

        if menu_item:
            # Рекурсивная фильтрация и обрезка по глубине
            menu_item = self._filter_and_limit_depth(menu_item, access_level, max_depth, current_depth=0)

        return menu_item

    def _filter_and_limit_depth(
        self, menu_item: MenuItem, access_level: AccessLevel, max_depth: int, current_depth: int
    ) -> MenuItem:
        """Рекурсивная фильтрация и ограничение глубины загрузки."""
        # Фильтрация дочерних элементов по доступу
        filtered_children = [
            child
            for child in menu_item.children
            if child.is_active and (access_level == AccessLevel.PREMIUM or child.access_level == AccessLevel.FREE)
        ]

        # Если достигли максимальной глубины, обнуляем children
        if current_depth >= max_depth:
            for child in filtered_children:
                child.children = []
        else:
            # Рекурсивно обрабатываем дочерние элементы
            for child in filtered_children:
                self._filter_and_limit_depth(child, access_level, max_depth, current_depth + 1)

        menu_item.children = filtered_children
        return menu_item

    async def increment_view_count(self, db: AsyncSession, menu_id: int) -> None:
        """Увеличить счетчик просмотров."""
        from sqlalchemy import update

        await db.execute(update(MenuItem).where(MenuItem.id == menu_id).values(view_count=MenuItem.view_count + 1))
        await db.flush()


menu_crud = MenuItemCRUD()
