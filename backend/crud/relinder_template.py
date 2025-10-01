"""CRUD операции для пунктов меню."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import ReminderTemplate

from .base import BaseCRUD


class ReminderTemplateCRUD(BaseCRUD[ReminderTemplate, dict, dict]):
    """CRUD операции для шаблона напоминаний."""

    def __init__(self):
        """Инициализация CRUD для шаблона напоминаний."""
        super().__init__(ReminderTemplate)

    async def get_last_active(
        self,
        db: AsyncSession,
    ) -> Optional[ReminderTemplate]:
        """Получить последний активный шаблон."""
        query = select(ReminderTemplate).where(ReminderTemplate.is_active).order_by(desc(ReminderTemplate.updated_at))

        result = await db.execute(query)
        print("0", type(result), result)
        print("model", self.model)
        item = result.scalars().first()
        print("1", item)
        return item


reminder_template_crud = ReminderTemplateCRUD()
