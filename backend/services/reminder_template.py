"""Сервис для работы с шаблонами напоминаний."""

from __future__ import annotations

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
        items_data = [AdminReminderTemplateResponse.model_validate(item) for item in items]
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
        reminder_template_validator.validate_template_input_data(data=request.model_dump())
        template = await reminder_template_crud.create(db=db, obj_in=request)
        return AdminReminderTemplateResponse.model_validate(template)

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
        reminder_template_validator.validate_template_input_data(data=request.model_dump(exclude_unset=True))

        template = await reminder_template_crud.get(db=db, id=template_id)
        reminder_template_validator.validate_template_exists(template=template)

        updatet_template = await reminder_template_crud.update(db=db, obj_in=request, db_obj=template)
        return AdminReminderTemplateResponse.model_validate(updatet_template)

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
        template = await reminder_template_crud.get(db=db, id=template_id)
        reminder_template_validator.validate_template_exists(template=template)
        
        await reminder_template_crud.remove(db=db, id=template_id)

    async def get_last_active_template(
        self,
        db: AsyncSession,
    ) -> BotReminderTemplateResponse:
        """Получить последний активный шаблон.

        Args:
            db: Сессия базы данных

        Returns:
            Шаблон напоминаний
        """
        template = await reminder_template_crud.get_last_active(db=db)
        if not template:
            return {}
        return BotReminderTemplateResponse(template)


reminder_template_service = ReminderTemplateService()
