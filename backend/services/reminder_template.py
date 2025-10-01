"""Сервис для работы с шаблонами напоминаний."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import reminder_template_crud
from backend.schemas.admin import (
    AdminReminderTemplateCreate,
    AdminReminderTemplateListResponse,
    AdminReminderTemplateResponse,
    AdminReminderTemplateUpdate,
)
from backend.schemas.bot import BotReminderTemplateResponse
from backend.validators import reminder_template_validator


class ReminderTemplateService:
    """Сервис для работы с шаблонами напоминаний."""

    def __init__(self):
        """Инициализация сервиса Reminder Template."""

    async def get_reminder_templates(
        self,
        db: AsyncSession,
    ) -> AdminReminderTemplateListResponse:
        """Получение всех шаблонов напоминаний.

        Args:
            db: Сессия базы данных

        Returns:
            Список шаблонов напоминаний
        """
        items = await reminder_template_crud.get_multi(db=db)
        print("1", items)
        items_data = [AdminReminderTemplateResponse.model_validate(item) for item in items]
        print("2", items_data)
        return AdminReminderTemplateListResponse(items=items_data)

    async def create_reminder_template(
        self,
        request: AdminReminderTemplateCreate,
        db: AsyncSession,
    ) -> AdminReminderTemplateResponse:
        """Создание шаблона напоминания.

        Args:
            request: Данные шаблона для создания
            db: Сессия базы данных

        Returns:
            Ответ с созданым шаблоном напоминаний
        """
        template = await reminder_template_crud.create(db=db, obj_in=request)
        return template

    async def update_reminder_template(
        self,
        template_id: int,
        request: AdminReminderTemplateUpdate,
        db: AsyncSession,
    ) -> AdminReminderTemplateResponse:
        """Обновление шаблона напоминания.

        Args:
            template_id: ID шаблона
            request: Данные шаблона для обновления
            db: Сессия базы данных

        Returns:
            Ответ с созданым шаблоном напоминаний
        """
        template = await reminder_template_crud.get(db=db, id=template_id)
        return await reminder_template_crud.update(db=db, obj_in=request, db_obj=template)

    async def delete_reminder_template(
        self,
        template_id: int,
        db: AsyncSession,
    ) -> None:
        """Удаление шаблона напоминания.

        Args:
            template_id: ID шаблона
            db: Сессия базы данных

        Returns:
            None
        """
        print("templ_id", template_id)
        template = await reminder_template_crud.get(db=db, id=template_id)
        print("got_template_for delete", template)
        await reminder_template_crud.remove(db=db, id=template_id)

    async def get_last_active_template(
        self,
        db: AsyncSession,
    ) -> Optional[BotReminderTemplateResponse | None]:
        """Получить последний активный шаблон.

        Args:
            db: Сессия базы данных

        Returns:
            Шаблон напоминаний
        """
        item = await reminder_template_crud.get_last_active(db=db)
        print("2", item)
        return item


reminder_template_service = ReminderTemplateService()
