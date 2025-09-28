"""CRUD операции для пунктов меню."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .base import BaseCRUD
from models import MenuItem
from models.enums import AccessLevel


class MenuItemCRUD(BaseCRUD[MenuItem, dict, dict]):
    """CRUD операции для пунктов меню."""

    def __init__(self):
        super().__init__(MenuItem)

    async def get_by_parent_id(
        self, 
        db: AsyncSession, 
        parent_id: Optional[int] = None,
        is_active: bool = True
    ) -> List[MenuItem]:
        """Получить дочерние пункты меню."""
        query = select(MenuItem).where(MenuItem.parent_id == parent_id)
        
        if is_active:
            query = query.where(MenuItem.is_active == True)
        
        query = query.order_by(MenuItem.id)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items

    async def get_with_children(
        self, 
        db: AsyncSession, 
        parent_id: Optional[int] = None,
        access_level: AccessLevel = AccessLevel.FREE
    ) -> List[MenuItem]:
        """Получить пункты меню с дочерними элементами."""
        query = select(MenuItem).where(
            MenuItem.parent_id == parent_id,
            MenuItem.is_active == True,
            MenuItem.access_level == access_level
        ).order_by(MenuItem.id)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        # Простая загрузка дочерних элементов (без рекурсии)
        for item in items:
            children_query = select(MenuItem).where(
                MenuItem.parent_id == item.id,
                MenuItem.is_active == True,
                MenuItem.access_level == access_level
            ).order_by(MenuItem.id)
            
            children_result = await db.execute(children_query)
            children = children_result.scalars().all()
            
            # Устанавливаем пустой список children для каждого дочернего элемента
            for child in children:
                child.children = []
            
            item.children = children
        
        return items

    async def get_with_content(
        self, 
        db: AsyncSession, 
        menu_id: int
    ) -> Optional[MenuItem]:
        """Получить пункт меню с контентом."""
        query = select(MenuItem).options(
            selectinload(MenuItem.content_files)
        ).where(MenuItem.id == menu_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def increment_view_count(self, db: AsyncSession, menu_id: int) -> None:
        """Увеличить счетчик просмотров."""
        item = await self.get(db, menu_id)
        if item:
            item.view_count += 1
            await db.commit()


menu_crud = MenuItemCRUD()
