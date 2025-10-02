"""Простой сервис шаблонов для MVP."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import reminder_template_crud
from backend.models import ReminderTemplate
from backend.schemas.admin.reminder_template import (
    AdminReminderTemplateCreate,
    AdminReminderTemplateListResponse,
    AdminReminderTemplateResponse,
    AdminReminderTemplateUpdate,
)
from backend.schemas.bot.reminder_template import BotReminderTemplateResponse
from backend.validators.reminder_template import reminder_template_validator


class ReminderTemplateService:
    """Простой сервис для шаблонов."""

    def __init__(self):
        """Инициализация сервиса для шаблонов напоминаний."""
        self.validator = reminder_template_validator

    async def get_default_template(self, db: AsyncSession) -> Optional[ReminderTemplate]:
        """Получить шаблон по умолчанию."""
        template = await reminder_template_crud.get_default_template(db)

        # Если шаблона нет - создаем по умолчанию
        if not template:
            template = await reminder_template_crud.create_default_template(db)

        return template

    def personalize_message(self, template: str, first_name: str) -> str:
        """Персонализировать сообщение шаблона."""
        return template.replace("{first_name}", first_name)

    async def get_admin_templates(self, db: AsyncSession) -> AdminReminderTemplateListResponse:
        """Получить все шаблоны для админов."""
        templates = await reminder_template_crud.get_active_templates(db)

        templates_data = [
            AdminReminderTemplateResponse(
                id=t.id,
                name=t.name,
                message_template=t.message_template,
                is_active=t.is_active,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in templates
        ]

        return AdminReminderTemplateListResponse(templates=templates_data)

    async def create_admin_template(
        self, db: AsyncSession, request: AdminReminderTemplateCreate
    ) -> AdminReminderTemplateResponse:
        """Создать новый шаблон."""
        template_data = {
            "name": request.name,
            "message_template": request.message_template,
            "is_active": True,
        }

        template = await reminder_template_crud.create(db, template_data)
        return AdminReminderTemplateResponse.model_validate(template)

    async def update_admin_template(
        self, db: AsyncSession, template_id: int, request: AdminReminderTemplateUpdate
    ) -> AdminReminderTemplateResponse:
        """Обновить шаблон."""
        template = await reminder_template_crud.get(db, template_id)
        self.validator.validate_template_exists_for_id(template, template_id)

        update_data = request.model_dump(exclude_unset=True)
        updated_template = await reminder_template_crud.update(db, db_obj=template, obj_in=update_data)

        return AdminReminderTemplateResponse.model_validate(updated_template)

    async def activate_template(self, db: AsyncSession, template_id: int) -> AdminReminderTemplateResponse:
        """Активировать шаблон."""
        template = await reminder_template_crud.get(db, template_id)
        self.validator.validate_template_exists_for_id(template, template_id)

        await reminder_template_crud.update(db, db_obj=template, obj_in={"is_active": True})

        updated_template = await reminder_template_crud.get(db, template_id)
        return AdminReminderTemplateResponse.model_validate(updated_template)

    async def deactivate_template(self, db: AsyncSession, template_id: int) -> AdminReminderTemplateResponse:
        """Деактивировать шаблон."""
        template = await reminder_template_crud.get(db, template_id)
        self.validator.validate_template_exists_for_id(template, template_id)

        await reminder_template_crud.update(db, db_obj=template, obj_in={"is_active": False})

        updated_template = await reminder_template_crud.get(db, template_id)
        return AdminReminderTemplateResponse.model_validate(updated_template)

    async def delete_template(self, db: AsyncSession, template_id: int) -> None:
        """Удалить шаблон."""
        template = await reminder_template_crud.get(db, template_id)
        self.validator.validate_template_exists_for_id(template, template_id)

        await reminder_template_crud.remove(db, id=template_id)

    async def get_default_template_response(self, db: AsyncSession) -> BotReminderTemplateResponse:
        """Получить шаблон по умолчанию для Bot API."""
        template = await self.get_default_template(db)

        return BotReminderTemplateResponse(
            id=template.id,
            name=template.name,
            message_template=template.message_template,
            created_at=template.created_at,
        )


reminder_template_service = ReminderTemplateService()
