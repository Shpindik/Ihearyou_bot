"""CRUD операции для файлов контента."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseCRUD
from models import ContentFile


class ContentFileCRUD(BaseCRUD[ContentFile, dict, dict]):
    """CRUD операции для файлов контента."""

    def __init__(self):
        super().__init__(ContentFile)

    async def get_by_menu_item(
        self, 
        db: AsyncSession, 
        menu_item_id: int
    ) -> List[ContentFile]:
        """Получить файлы контента для пункта меню."""
        query = select(ContentFile).where(
            ContentFile.menu_item_id == menu_item_id
        ).order_by(ContentFile.sort_order, ContentFile.id)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def get_primary_content(
        self, 
        db: AsyncSession, 
        menu_item_id: int
    ) -> Optional[ContentFile]:
        """Получить основной контент для пункта меню."""
        query = select(ContentFile).where(
            ContentFile.menu_item_id == menu_item_id,
            ContentFile.is_primary == True
        )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()


content_file_crud = ContentFileCRUD()
