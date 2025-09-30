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
    ) -> List[MenuItem]:
        """Получить дочерние пункты меню с их детьми одним запросом."""
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

        for item in items:
            if access_level is not None:
                filtered_children = [
                    child
                    for child in item.children
                    if child.is_active
                    and (access_level == AccessLevel.PREMIUM or child.access_level == AccessLevel.FREE)
                ]
                item.children = filtered_children

            for child in item.children:
                child.children = []

        return items

    async def get_with_content(self, db: AsyncSession, menu_id: int) -> Optional[MenuItem]:
        """Получить пункт меню с контентом."""
        query = select(MenuItem).options(selectinload(MenuItem.content_files)).where(MenuItem.id == menu_id)

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_with_content_and_children(
        self, db: AsyncSession, menu_id: int, access_level: AccessLevel
    ) -> Optional[MenuItem]:
        """Получить пункт меню с контентом и дочерними элементами одним запросом."""
        query = (
            select(MenuItem)
            .options(selectinload(MenuItem.content_files), selectinload(MenuItem.children))
            .where(MenuItem.id == menu_id, MenuItem.is_active)
        )

        result = await db.execute(query)
        menu_item = result.scalar_one_or_none()

        if menu_item:
            filtered_children = [
                child
                for child in menu_item.children
                if child.is_active and (access_level == AccessLevel.PREMIUM or child.access_level == AccessLevel.FREE)
            ]
            menu_item.children = filtered_children

            for child in menu_item.children:
                child.children = []

        return menu_item

    async def increment_view_count(self, db: AsyncSession, menu_id: int) -> None:
        """Увеличить счетчик просмотров."""
        from sqlalchemy import update

        await db.execute(update(MenuItem).where(MenuItem.id == menu_id).values(view_count=MenuItem.view_count + 1))
        await db.flush()


menu_crud = MenuItemCRUD()
