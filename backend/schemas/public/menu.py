"""Публичные схемы для меню бота."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.models.enums import AccessLevel, ContentType, ItemType


class MenuItemResponse(BaseModel):
    """Схема ответа пункта меню для GET /api/v1/menu-items."""

    id: int = Field(..., description="ID пункта меню")
    title: str = Field(..., description="Название пункта меню")
    description: Optional[str] = Field(None, description="Описание пункта меню")
    parent_id: Optional[int] = Field(None, description="ID родительского пункта")
    bot_message: Optional[str] = Field(None, description="Сообщение бота")
    is_active: bool = Field(..., description="Активен ли пункт")
    access_level: AccessLevel = Field(..., description="Уровень доступа")
    item_type: ItemType = Field(..., description="Тип пункта меню")
    children: list["MenuItemResponse"] = Field(default_factory=list, description="Дочерние пункты")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Слуховые аппараты",
                "description": "Информация о слуховых аппаратах",
                "parent_id": None,
                "bot_message": "Выберите интересующий вас раздел:",
                "is_active": True,
                "access_level": "free",
                "item_type": "navigation",
                "children": [
                    {
                        "id": 2,
                        "title": "Типы слуховых аппаратов",
                        "description": "Обзор различных типов",
                        "parent_id": 1,
                        "bot_message": "Выберите тип:",
                        "is_active": True,
                        "access_level": "free",
                        "item_type": "content",
                        "children": [],
                    }
                ],
            }
        },
    )


class MenuItemListResponse(BaseModel):
    """Схема ответа списка пунктов меню для GET /api/v1/menu-items."""

    items: list[MenuItemResponse] = Field(..., description="Список пунктов меню")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 1,
                        "title": "Слуховые аппараты",
                        "description": "Информация о слуховых аппаратах",
                        "parent_id": None,
                        "bot_message": "Выберите интересующий вас раздел:",
                        "is_active": True,
                        "access_level": "free",
                        "item_type": "navigation",
                        "children": [
                            {
                                "id": 2,
                                "title": "Типы слуховых аппаратов",
                                "description": "Обзор различных типов",
                                "parent_id": 1,
                                "bot_message": "Выберите тип:",
                                "is_active": True,
                                "access_level": "free",
                                "item_type": "content",
                                "children": [],
                            }
                        ],
                    }
                ]
            }
        }
    )


class ContentFileResponse(BaseModel):
    """Схема данных файла контента."""

    content_type: ContentType = Field(..., description="Тип контента")

    # Контент для пользователей
    caption: Optional[str] = Field(None, description="Подпись к медиафайлу")
    text_content: Optional[str] = Field(None, description="Текстовый контент")
    external_url: Optional[str] = Field(None, description="URL внешнего ресурса")
    web_app_short_name: Optional[str] = Field(None, description="Короткое имя Web App")

    # Метаданные файла (безопасные для публичного доступа)
    file_size: Optional[int] = Field(None, description="Размер файла в байтах")
    mime_type: Optional[str] = Field(None, description="MIME тип файла")
    width: Optional[int] = Field(None, description="Ширина изображения/видео")
    height: Optional[int] = Field(None, description="Высота изображения/видео")
    duration: Optional[int] = Field(None, description="Длительность видео/аудио в секундах")

    model_config = ConfigDict(from_attributes=True)


class MenuContentResponse(BaseModel):
    """Схема ответа контента пункта меню для GET /api/v1/menu-items/{id}/content."""

    id: int = Field(..., description="ID пункта меню")
    title: str = Field(..., description="Название пункта меню")
    description: Optional[str] = Field(None, description="Описание пункта меню")
    bot_message: Optional[str] = Field(None, description="Сообщение бота")
    content_files: list[ContentFileResponse] = Field(..., description="Файлы контента")
    children: list[MenuItemResponse] = Field(default_factory=list, description="Дочерние пункты")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Слуховые аппараты",
                "description": "Информация о слуховых аппаратах",
                "bot_message": "Вот полезная информация о слуховых аппаратах:",
                "content_files": [
                    {
                        "content_type": "text",
                        "caption": None,
                        "text_content": "Слуховые аппараты помогают улучшить качество слуха и облегчить привыкание к звуковой среде...",
                        "external_url": None,
                        "web_app_short_name": None,
                        "file_size": None,
                        "mime_type": None,
                        "width": None,
                        "height": None,
                        "duration": None,
                    },
                    {
                        "content_type": "external_url",
                        "caption": "Изображение слухового аппарата",
                        "text_content": None,
                        "external_url": "https://example.com/image.jpg",
                        "web_app_short_name": None,
                        "file_size": 1024000,
                        "mime_type": "image/jpeg",
                        "width": 1920,
                        "height": 1080,
                        "duration": None,
                    },
                ],
            }
        },
    )
