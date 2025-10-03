"""Сервис для работы с файлами контента."""

from __future__ import annotations

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.content_file import content_file_crud
from backend.crud.menu_item import menu_item_crud
from backend.schemas.admin.menu import AdminContentFileCreate, AdminContentFileResponse, AdminContentFileUpdate
from backend.validators.content_file import content_file_validator


class ContentFileService:
    """Сервис для работы с файлами контента."""

    def __init__(self):
        """Инициализация сервиса Content File."""
        self.content_file_crud = content_file_crud
        self.menu_item_crud = menu_item_crud
        self.validator = content_file_validator

    async def get_content_files(self, db: AsyncSession, menu_item_id: int) -> List[AdminContentFileResponse]:
        """Получение файлов контента для пункта меню.

        Args:
            db: Сессия базы данных
            menu_item_id: ID пункта меню

        Returns:
            Список файлов контента (теперь всегда один элемент или пустой список)
        """
        menu_item = await self.menu_item_crud.get(db, menu_item_id)
        self.validator.validate_menu_item_exists(menu_item)

        content_file = await self.content_file_crud.get_by_menu_item_id(db, menu_item_id)

        if content_file:
            return [
                AdminContentFileResponse(
                    id=content_file.id,
                    menu_item_id=content_file.menu_item_id,
                    content_type=content_file.content_type,
                    telegram_file_id=content_file.telegram_file_id,
                    caption=content_file.caption,
                    text_content=content_file.text_content,
                    external_url=content_file.external_url,
                    local_file_path=content_file.local_file_path,
                    file_size=content_file.file_size,
                    mime_type=content_file.mime_type,
                    width=content_file.width,
                    height=content_file.height,
                    duration=content_file.duration,
                    thumbnail_telegram_file_id=content_file.thumbnail_telegram_file_id,
                    created_at=content_file.created_at,
                    updated_at=content_file.updated_at,
                )
            ]
        return []

    async def create_content_file(
        self, db: AsyncSession, menu_item_id: int, request: AdminContentFileCreate
    ) -> AdminContentFileResponse:
        """Создание файла контента.

        Args:
            db: Сессия базы данных
            menu_item_id: ID пункта меню
            request: Данные для создания файла

        Returns:
            Созданный файл контента
        """
        menu_item = await self.menu_item_crud.get(db, menu_item_id)
        self.validator.validate_menu_item_exists(menu_item)

        existing_content = await self.content_file_crud.get_by_menu_item_id(db, menu_item_id)
        self.validator.validate_one_content_per_menu_item(menu_item_id, existing_content)

        self.validator.validate_content_type_requirements(
            request.content_type,
            request.telegram_file_id,
            request.text_content,
            request.external_url,
            request.local_file_path,
        )

        if request.caption:
            self.validator.validate_caption_length(request.caption)

        if request.telegram_file_id:
            self.validator.validate_telegram_file_id_format(request.telegram_file_id)

        if request.external_url:
            self.validator.validate_url_format(request.external_url)

        if request.file_size:
            self.validator.validate_file_size(request.file_size)

        content_file_data = request.model_dump()
        content_file_data["menu_item_id"] = menu_item_id
        content_file = await self.content_file_crud.create(db, obj_in=content_file_data)

        return AdminContentFileResponse(
            id=content_file.id,
            menu_item_id=content_file.menu_item_id,
            content_type=content_file.content_type,
            telegram_file_id=content_file.telegram_file_id,
            caption=content_file.caption,
            text_content=content_file.text_content,
            external_url=content_file.external_url,
            local_file_path=content_file.local_file_path,
            file_size=content_file.file_size,
            mime_type=content_file.mime_type,
            width=content_file.width,
            height=content_file.height,
            duration=content_file.duration,
            thumbnail_telegram_file_id=content_file.thumbnail_telegram_file_id,
            created_at=content_file.created_at,
            updated_at=content_file.updated_at,
        )

    async def update_content_file(
        self, db: AsyncSession, file_id: int, request: AdminContentFileUpdate
    ) -> AdminContentFileResponse:
        """Обновление файла контента.

        Args:
            db: Сессия базы данных
            file_id: ID файла контента
            request: Данные для обновления

        Returns:
            Обновленный файл контента
        """
        content_file = await self.content_file_crud.get(db, file_id)
        self.validator.validate_content_file_exists(content_file)

        if request.content_type:
            self.validator.validate_content_type_requirements(
                request.content_type,
                request.telegram_file_id or content_file.telegram_file_id,
                request.text_content or content_file.text_content,
                request.external_url or content_file.external_url,
                request.local_file_path or content_file.local_file_path,
            )

        if request.file_size is not None:
            self.validator.validate_file_size(request.file_size)

        if request.external_url is not None:
            self.validator.validate_url_format(request.external_url)

        if request.caption is not None:
            self.validator.validate_caption_length(request.caption)

        if request.telegram_file_id is not None:
            self.validator.validate_telegram_file_id_format(request.telegram_file_id)

        updated_file = await self.content_file_crud.update(db, db_obj=content_file, obj_in=request)

        return AdminContentFileResponse(
            id=updated_file.id,
            menu_item_id=updated_file.menu_item_id,
            content_type=updated_file.content_type,
            telegram_file_id=updated_file.telegram_file_id,
            caption=updated_file.caption,
            text_content=updated_file.text_content,
            external_url=updated_file.external_url,
            local_file_path=updated_file.local_file_path,
            file_size=updated_file.file_size,
            mime_type=updated_file.mime_type,
            width=updated_file.width,
            height=updated_file.height,
            duration=updated_file.duration,
            thumbnail_telegram_file_id=updated_file.thumbnail_telegram_file_id,
            created_at=updated_file.created_at,
            updated_at=updated_file.updated_at,
        )

    async def delete_content_file(self, db: AsyncSession, file_id: int) -> None:
        """Удаление файла контента.

        Args:
            db: Сессия базы данных
            file_id: ID файла контента
        """
        content_file = await self.content_file_crud.get(db, file_id)
        self.validator.validate_content_file_exists(content_file)

        await self.content_file_crud.remove(db, id=file_id)


content_file_service = ContentFileService()
