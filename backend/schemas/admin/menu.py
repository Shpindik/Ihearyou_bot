"""Административные схемы для управления меню."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.models.enums import AccessLevel, ContentType, ItemType


class AdminMenuItemResponse(BaseModel):
    """Схема данных пункта меню для админ API."""

    id: int = Field(..., description="ID пункта меню")
    title: str = Field(..., description="Название пункта меню")
    description: Optional[str] = Field(None, description="Описание пункта меню")
    parent_id: Optional[int] = Field(None, description="ID родительского пункта")
    bot_message: Optional[str] = Field(None, description="Сообщение бота")
    is_active: bool = Field(..., description="Активен ли пункт")
    access_level: AccessLevel = Field(..., description="Уровень доступа")
    item_type: ItemType = Field(..., description="Тип пункта меню")
    view_count: int = Field(..., description="Количество просмотров")
    download_count: int = Field(..., description="Количество скачиваний")
    rating_sum: int = Field(..., description="Сумма оценок")
    rating_count: int = Field(..., description="Количество оценок")
    average_rating: Optional[float] = Field(None, description="Средняя оценка")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")

    model_config = ConfigDict(from_attributes=True)


class AdminMenuItemCreate(BaseModel):
    """Схема запроса создания пункта меню для POST /api/v1/admin/menu-items."""

    title: str = Field(..., min_length=1, max_length=255, description="Название пункта меню")
    description: Optional[str] = Field(None, description="Описание пункта меню")
    parent_id: Optional[int] = Field(None, description="ID родительского пункта")
    bot_message: Optional[str] = Field(None, description="Сообщение бота")
    access_level: AccessLevel = Field(default=AccessLevel.FREE, description="Уровень доступа")
    is_active: bool = Field(default=True, description="Активен ли пункт")
    item_type: ItemType = Field(default=ItemType.NAVIGATION, description="Тип пункта меню")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Новый раздел",
                "description": "Описание нового раздела",
                "parent_id": 1,
                "bot_message": "Сообщение бота для этого раздела",
                "access_level": "free",
                "is_active": True,
            }
        }
    )


class AdminMenuItemUpdate(BaseModel):
    """Схема запроса обновления пункта меню для PUT /api/v1/admin/menu-items/{id}."""

    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Название пункта меню")
    description: Optional[str] = Field(None, description="Описание пункта меню")
    parent_id: Optional[int] = Field(None, description="ID родительского пункта")
    bot_message: Optional[str] = Field(None, description="Сообщение бота")
    access_level: Optional[AccessLevel] = Field(None, description="Уровень доступа")
    is_active: Optional[bool] = Field(None, description="Активен ли пункт")
    item_type: Optional[ItemType] = Field(None, description="Тип пункта меню")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Обновленное название",
                "description": "Обновленное описание",
                "bot_message": "Обновленное сообщение бота",
                "access_level": "premium",
                "is_active": True,
            }
        }
    )


class AdminMenuItemListResponse(BaseModel):
    """Схема ответа списка пунктов меню для GET /api/v1/admin/menu-items."""

    items: List[AdminMenuItemResponse] = Field(..., description="Список пунктов меню")
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Текущая страница")
    limit: int = Field(..., description="Лимит на странице")
    pages: int = Field(..., description="Общее количество страниц")

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
                        "view_count": 150,
                        "download_count": 45,
                        "rating_sum": 450,
                        "rating_count": 100,
                        "average_rating": 4.5,
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-15T16:00:00Z",
                    }
                ],
                "total": 50,
                "page": 1,
                "limit": 20,
                "pages": 3,
            }
        }
    )


class AdminContentFileResponse(BaseModel):
    """Схема данных файла контента для админ API."""

    id: int = Field(..., description="ID файла")
    menu_item_id: int = Field(..., description="ID пункта меню")
    content_type: ContentType = Field(..., description="Тип контента")
    telegram_file_id: Optional[str] = Field(None, max_length=255, description="File ID от Telegram")
    caption: Optional[str] = Field(None, description="Подпись к медиафайлу")
    text_content: Optional[str] = Field(None, description="Текстовый контент")
    external_url: Optional[str] = Field(None, description="URL внешнего ресурса")
    local_file_path: Optional[str] = Field(None, description="Путь к локальному файлу")
    web_app_short_name: Optional[str] = Field(None, max_length=255, description="Короткое имя Web App")

    # Метаданные
    file_size: Optional[int] = Field(None, description="Размер файла")
    mime_type: Optional[str] = Field(None, max_length=100, description="MIME тип")
    width: Optional[int] = Field(None, description="Ширина изображения/видео")
    height: Optional[int] = Field(None, description="Высота изображения/видео")
    duration: Optional[int] = Field(None, description="Длительность видео/аудио в секундах")
    thumbnail_telegram_file_id: Optional[str] = Field(None, max_length=255, description="File ID превью от Telegram")

    # Аудит
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")

    model_config = ConfigDict(from_attributes=True)


class AdminContentFileCreate(BaseModel):
    """Схема запроса создания файла контента для POST /api/v1/admin/menu-items/{id}/content-files."""

    content_type: ContentType = Field(..., description="Тип контента")
    telegram_file_id: Optional[str] = Field(None, max_length=255, description="File ID от Telegram")
    caption: Optional[str] = Field(None, description="Подпись к медиафайлу (до 1024 символов)")
    text_content: Optional[str] = Field(None, description="Текстовый контент")
    external_url: Optional[str] = Field(None, description="URL внешнего ресурса")
    local_file_path: Optional[str] = Field(None, description="Путь к локальному файлу")
    web_app_short_name: Optional[str] = Field(None, max_length=255, description="Короткое имя Web App")

    # Метаданные
    file_size: Optional[int] = Field(None, description="Размер файла")
    mime_type: Optional[str] = Field(None, max_length=100, description="MIME тип")
    width: Optional[int] = Field(None, description="Ширина изображения/видео")
    height: Optional[int] = Field(None, description="Высота изображения/видео")
    duration: Optional[int] = Field(None, description="Длительность видео/аудио в секундах")
    thumbnail_telegram_file_id: Optional[str] = Field(None, max_length=255, description="File ID превью от Telegram")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content_type": "text",
                "text_content": "Новый текстовый контент",
            }
        }
    )


class AdminContentFileUpdate(BaseModel):
    """Схема запроса обновления файла контента для PUT /api/v1/admin/menu-items/content-files/{file_id}."""

    content_type: Optional[ContentType] = Field(None, description="Тип контента")
    telegram_file_id: Optional[str] = Field(None, max_length=255, description="File ID от Telegram")
    caption: Optional[str] = Field(None, description="Подпись к медиафайлу (до 1024 символов)")
    text_content: Optional[str] = Field(None, description="Текстовый контент")
    external_url: Optional[str] = Field(None, description="URL внешнего ресурса")
    local_file_path: Optional[str] = Field(None, description="Путь к локальному файлу")
    web_app_short_name: Optional[str] = Field(None, max_length=255, description="Короткое имя Web App")

    # Метаданные
    file_size: Optional[int] = Field(None, description="Размер файла")
    mime_type: Optional[str] = Field(None, max_length=100, description="MIME тип")
    width: Optional[int] = Field(None, description="Ширина изображения/видео")
    height: Optional[int] = Field(None, description="Высота изображения/видео")
    duration: Optional[int] = Field(None, description="Длительность видео/аудио в секундах")
    thumbnail_telegram_file_id: Optional[str] = Field(None, max_length=255, description="File ID превью от Telegram")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text_content": "Обновленный текстовый контент",
            }
        }
    )
