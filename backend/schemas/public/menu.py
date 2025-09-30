"""Публичные схемы для меню бота."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.models.enums import AccessLevel, ContentType


class MenuItemResponse(BaseModel):
    """Схема ответа пункта меню для GET /api/v1/menu-items."""

    id: int = Field(..., description="ID пункта меню")
    title: str = Field(..., description="Название пункта меню")
    description: Optional[str] = Field(None, description="Описание пункта меню")
    parent_id: Optional[int] = Field(None, description="ID родительского пункта")
    bot_message: Optional[str] = Field(None, description="Сообщение бота")
    is_active: bool = Field(..., description="Активен ли пункт")
    access_level: AccessLevel = Field(..., description="Уровень доступа")
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
                "children": [
                    {
                        "id": 2,
                        "title": "Типы слуховых аппаратов",
                        "description": "Обзор различных типов",
                        "parent_id": 1,
                        "bot_message": "Выберите тип:",
                        "is_active": True,
                        "access_level": "free",
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
                        "children": [
                            {
                                "id": 2,
                                "title": "Типы слуховых аппаратов",
                                "description": "Обзор различных типов",
                                "parent_id": 1,
                                "bot_message": "Выберите тип:",
                                "is_active": True,
                                "access_level": "free",
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

    id: int = Field(..., description="ID файла контента")
    menu_item_id: int = Field(..., description="ID пункта меню")
    content_type: ContentType = Field(..., description="Тип контента")
    content_text: Optional[str] = Field(None, description="Текстовый контент")
    content_url: Optional[str] = Field(None, description="URL контента")
    file_path: Optional[str] = Field(None, description="Путь к файлу")
    file_size: Optional[int] = Field(None, description="Размер файла в байтах")
    mime_type: Optional[str] = Field(None, description="MIME тип файла")
    thumbnail_url: Optional[str] = Field(None, description="URL превью")
    is_primary: bool = Field(..., description="Основной ли файл")
    sort_order: int = Field(..., description="Порядок сортировки")

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
                        "id": 1,
                        "menu_item_id": 1,
                        "content_type": "text",
                        "content_text": "Слуховые аппараты помогают...",
                        "content_url": None,
                        "file_path": None,
                        "file_size": None,
                        "mime_type": None,
                        "thumbnail_url": None,
                        "is_primary": True,
                        "sort_order": 1,
                    },
                    {
                        "id": 2,
                        "menu_item_id": 1,
                        "content_type": "image",
                        "content_text": None,
                        "content_url": "https://example.com/image.jpg",
                        "file_path": None,
                        "file_size": None,
                        "mime_type": "image/jpeg",
                        "thumbnail_url": "https://example.com/thumb.jpg",
                        "is_primary": False,
                        "sort_order": 2,
                    },
                ],
            }
        },
    )
