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

    async def get_all_templates(self, db: AsyncSession) -> List[MessageTemplate]:
        """Получить активные шаблоны сообщений."""
        query = select(MessageTemplate)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_default_template(self, db: AsyncSession) -> Optional[MessageTemplate]:
        """Получить шаблон по умолчанию (самый новый активный)."""
        query = (
            select(MessageTemplate)
            .where(MessageTemplate.is_active)
            .order_by(MessageTemplate.created_at.desc())
            .limit(1)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()


message_template_crud = MessageTemplateCRUD()
