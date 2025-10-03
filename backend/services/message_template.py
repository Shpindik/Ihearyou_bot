"""Простой сервис шаблонов для MVP."""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import message_template_crud
from backend.models import MessageTemplate
from backend.schemas.admin.message_template import (
    AdminMessageTemplateCreate,
    AdminMessageTemplateListResponse,
    AdminMessageTemplateResponse,
    AdminMessageTemplateUpdate,
)
from backend.schemas.bot.message_template import BotMessageTemplateResponse
from backend.validators.message_template import message_template_validator


class MessageTemplateService:
    """Простой сервис для шаблонов."""

    def __init__(self):
        """Инициализация сервиса для шаблонов напоминаний."""
        self.validator = message_template_validator

    async def get_default_template(self, db: AsyncSession) -> MessageTemplate:
        """Получить шаблон по умолчанию."""
        template = await message_template_crud.get_default_template(db)

        # Если шаблона нет - создаем по умолчанию
        if not template:
            template = await self.create_default_template(db)

        return template

    def personalize_message(self, template: str, first_name: str) -> str:
        """Персонализировать сообщение шаблона."""
        return template.replace("{first_name}", first_name)

    async def get_admin_templates(self, db: AsyncSession) -> AdminMessageTemplateListResponse:
        """Получить все шаблоны для админов."""
        templates = await message_template_crud.get_all_templates(db)

        templates_data = [
            AdminMessageTemplateResponse(
                id=t.id,
                name=t.name,
                message_template=t.message_template,
                is_active=t.is_active,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in templates
        ]

        return AdminMessageTemplateListResponse(items=templates_data)

    async def create_admin_template(
        self, db: AsyncSession, request: AdminMessageTemplateCreate
    ) -> AdminMessageTemplateResponse:
        """Создать новый шаблон."""
        # template_data = {
        #     "name": request.name,
        #     "message_template": request.message_template,
        #     "is_active": True,
        # }

        template = await message_template_crud.create(db=db, obj_in=request)
        return AdminMessageTemplateResponse.model_validate(template)

    async def update_admin_template(
        self, db: AsyncSession, template_id: int, request: AdminMessageTemplateUpdate
    ) -> AdminMessageTemplateResponse:
        """Обновить шаблон."""
        template = await message_template_crud.get(db, template_id)
        self.validator.validate_template_exists_for_id(template, template_id)

        # update_data = request.model_dump(exclude_unset=True)
        updated_template = await message_template_crud.update(db, db_obj=template, obj_in=request)

        return AdminMessageTemplateResponse.model_validate(updated_template)

    async def activate_template(self, db: AsyncSession, template_id: int) -> AdminMessageTemplateResponse:
        """Активировать шаблон."""
        template = await message_template_crud.get(db, template_id)
        self.validator.validate_template_exists_for_id(template, template_id)

        await message_template_crud.update(db, db_obj=template, obj_in={"is_active": True})

        updated_template = await message_template_crud.get(db, template_id)
        return AdminMessageTemplateResponse.model_validate(updated_template)

    async def deactivate_template(self, db: AsyncSession, template_id: int) -> AdminMessageTemplateResponse:
        """Деактивировать шаблон."""
        template = await message_template_crud.get(db, template_id)
        self.validator.validate_template_exists_for_id(template, template_id)

        await message_template_crud.update(db, db_obj=template, obj_in={"is_active": False})

        updated_template = await message_template_crud.get(db, template_id)
        return AdminMessageTemplateResponse.model_validate(updated_template)

    async def delete_template(self, db: AsyncSession, template_id: int) -> None:
        """Удалить шаблон."""
        template = await message_template_crud.get(db, template_id)
        self.validator.validate_template_exists_for_id(template, template_id)

        await message_template_crud.remove(db, id=template_id)

    async def create_default_template(self, db: AsyncSession) -> MessageTemplate:
        """Создать шаблон по умолчанию."""
        default_data = AdminMessageTemplateCreate(
            name="Напоминание о возвращении",
            message_template="Привет, {first_name}! Мы по вам соскучились! Вернитесь к нам 🥰",
            is_active=True,
        )
        return await message_template_crud.create(db, default_data.model_dump())

    async def get_default_template_response(self, db: AsyncSession) -> BotMessageTemplateResponse:
        """Получить шаблон по умолчанию для Bot API."""
        template = await self.get_default_template(db)

        return BotMessageTemplateResponse(
            id=template.id,
            name=template.name,
            message_template=template.message_template,
            created_at=template.created_at,
        )


message_template_service = MessageTemplateService()
