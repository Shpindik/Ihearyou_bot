"""CRUD операции для файлов контента."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import ContentFile

from .base import BaseCRUD


class ContentFileCRUD(BaseCRUD[ContentFile, dict, dict]):
    """CRUD операции для файлов контента."""

    def __init__(self):
        """Инициализация CRUD для файлов контента."""
        super().__init__(ContentFile)

    async def get_by_menu_item_id(self, db: AsyncSession, menu_item_id: int) -> Optional[ContentFile]:
        """Получить файл контента для пункта меню (One-to-One)."""
        query = select(ContentFile).where(ContentFile.menu_item_id == menu_item_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()


content_file_crud = ContentFileCRUD()
