"""CRUD операции для пунктов меню."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import or_, select, update
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

    async def get_children_by_parent_id(
        self,
        db: AsyncSession,
        parent_id: int,
        is_active: bool = True,
        access_level: Optional[AccessLevel] = None,
    ) -> List[MenuItem]:
        """Получить только прямых детей родительского элемента.

        Args:
            db: Сессия базы данных
            parent_id: ID родительского элемента
            is_active: Фильтр по активности
            access_level: Уровень доступа пользователя
        """
        return await self.get_by_parent_id(db, parent_id, is_active, access_level)

    async def get_with_content(self, db: AsyncSession, menu_id: int) -> Optional[MenuItem]:
        """Получить пункт меню с контентом."""
        query = select(MenuItem).options(selectinload(MenuItem.content_files)).where(MenuItem.id == menu_id)

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_with_content_and_children(
        self, db: AsyncSession, menu_id: int, access_level: AccessLevel
    ) -> Optional[MenuItem]:
        """Получить пункт меню с контентом и прямыми дочерними элементами.

        Args:
            db: Сессия базы данных
            menu_id: ID пункта меню
            access_level: Уровень доступа пользователя
        """
        # Загружаем пункт меню с контентом
        query = (
            select(MenuItem).options(selectinload(MenuItem.content)).where(MenuItem.id == menu_id, MenuItem.is_active)
        )

        result = await db.execute(query)
        menu_item = result.scalar_one_or_none()

        if menu_item:
            # Загружаем дочерние элементы отдельным запросом для простоты
            children = await self.get_children_by_parent_id(db, menu_id, True, access_level)
            # Создаем простой объект без SQLAlchemy отношений
            menu_item._children = children

        return menu_item

    async def get_admin_menu_items(
        self,
        db: AsyncSession,
        parent_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        access_level: Optional[AccessLevel] = None,
    ) -> List[MenuItem]:
        """Получить пункты меню для администраторов с фильтрацией."""
        query = select(MenuItem)

        if parent_id is not None:
            query = query.where(MenuItem.parent_id == parent_id)

        if is_active is not None:
            query = query.where(MenuItem.is_active == is_active)

        if access_level is not None:
            query = query.where(MenuItem.access_level == access_level)

        query = query.order_by(MenuItem.parent_id, MenuItem.id)

        result = await db.execute(query)
        items = result.scalars().all()

        return items

    async def search_by_query(
        self,
        db: AsyncSession,
        query: str,
        access_level: AccessLevel,
        limit: int = 10,
    ) -> List[MenuItem]:
        """Поиск пунктов меню по запросу.

        Args:
            db: Сессия базы данных
            query: Поисковый запрос (уже валидированный)
            access_level: Уровень доступа пользователя
            limit: Максимальное количество результатов
        Returns:
            List[MenuItem]: Список найденных пунктов меню
        """
        if limit < 0:
            return []

        words = [w for w in query.strip().split() if w]
        if not words:
            return []

        conditions = []
        for word in words:
            pattern = f"%{word}%"
            conditions.append(
                or_(
                    MenuItem.title.ilike(pattern),
                    MenuItem.description.ilike(pattern),
                )
            )

        stmt = select(MenuItem).where(MenuItem.is_active, *conditions)

        if access_level == AccessLevel.FREE:
            stmt = stmt.where(MenuItem.access_level == AccessLevel.FREE)

        stmt = stmt.order_by(MenuItem.title.ilike(f"{query}%").desc(), MenuItem.id).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def increment_view_count(self, db: AsyncSession, *, menu_id: int) -> None:
        """Увеличить счетчик просмотров."""
        await db.execute(update(MenuItem).where(MenuItem.id == menu_id).values(view_count=MenuItem.view_count + 1))
        await db.commit()

    async def update_rating_stats(self, db: AsyncSession, *, menu_id: int, rating: int) -> None:
        """Обновить статистику оценок материалов.

        Args:
            db: Сессия базы данных
            menu_id: ID элемента меню
            rating: Оценка от 1 до 5

        """
        await db.execute(
            update(MenuItem)
            .where(MenuItem.id == menu_id)
            .values(
                rating_sum=MenuItem.rating_sum + rating,
                rating_count=MenuItem.rating_count + 1,
                average_rating=(MenuItem.rating_sum + rating) / (MenuItem.rating_count + 1),
            )
        )
        await db.commit()

    async def increment_download_count(self, db: AsyncSession, *, menu_id: int) -> None:
        """Увеличить счетчик скачиваний."""
        await db.execute(
            update(MenuItem).where(MenuItem.id == menu_id).values(download_count=MenuItem.download_count + 1)
        )
        await db.commit()


menu_item_crud = MenuItemCRUD()
