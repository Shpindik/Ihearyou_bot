"""Простой CRUD для шаблонов сообщений - MVP версия."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import MessageTemplate

from .base import BaseCRUD


class MessageTemplateCRUD(BaseCRUD[MessageTemplate, dict, dict]):
    """Простой CRUD для шаблонов сообщений."""

    def __init__(self):
        """Инициализация CRUD для шаблонов сообщений."""
        super().__init__(MessageTemplate)

    async def get_active_templates(self, db: AsyncSession) -> List[MessageTemplate]:
        """Получить активные шаблоны сообщений."""
        query = select(MessageTemplate).where(MessageTemplate.is_active)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_default_template(self, db: AsyncSession) -> Optional[MessageTemplate]:
        """Получить шаблон по умолчанию."""
        templates = await self.get_active_templates(db)
        return templates[0] if templates else None


message_template_crud = MessageTemplateCRUD()
