"""Простой CRUD для шаблонов напоминаний - MVP версия."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import ReminderTemplate

from .base import BaseCRUD


class ReminderTemplateCRUD(BaseCRUD[ReminderTemplate, dict, dict]):
    """Простой CRUD для шаблонов."""

    def __init__(self):
        """Инициализация CRUD для шаблонов."""
        super().__init__(ReminderTemplate)

    async def get_active_templates(self, db: AsyncSession) -> List[ReminderTemplate]:
        """Получить активные шаблоны."""
        query = select(ReminderTemplate).where(ReminderTemplate.is_active)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_default_template(self, db: AsyncSession) -> Optional[ReminderTemplate]:
        """Получить шаблон по умолчанию."""
        templates = await self.get_active_templates(db)
        return templates[0] if templates else None

    async def create_default_template(self, db: AsyncSession) -> ReminderTemplate:
        """Создать шаблон по умолчанию."""
        template_data = {
            "name": "Напоминание о возвращении",
            "message_template": "Привет, {first_name}! Мы по вам соскучились! Вернитесь к нам 🥰",
            "is_active": True,
        }
        return await self.create(db, template_data)


reminder_template_crud = ReminderTemplateCRUD()
