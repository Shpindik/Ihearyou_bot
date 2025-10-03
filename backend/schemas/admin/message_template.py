"""Pydantic схемы для шаблонов сообщений."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AdminMessageTemplateResponse(BaseModel):
    """Схема данных шаблона сообщения."""

    id: int = Field(..., description="ID шаблона")
    name: str = Field(..., description="Название шаблона")
    message_template: str = Field(..., description="Шаблон сообщения")
    is_active: bool = Field(..., description="Активен ли шаблон")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")

    model_config = ConfigDict(from_attributes=True)


class AdminMessageTemplateListResponse(BaseModel):
    """Схема ответа списка шаблонов сообщений для GET /api/v1/admin/message-templates."""

    items: list[AdminMessageTemplateResponse] = Field(..., description="Список шаблонов")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 1,
                        "name": "Еженедельное напоминание",
                        "message_template": "Привет! У нас есть новые материалы, которые могут быть полезны для вас.",
                        "is_active": True,
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-01T12:00:00Z",
                    }
                ]
            }
        }
    )


class AdminMessageTemplateCreate(BaseModel):
    """Схема запроса создания шаблона сообщения для POST /api/v1/admin/message-templates."""

    name: str = Field(..., min_length=3, max_length=255, description="Название шаблона")
    message_template: str = Field(..., min_length=20, max_length=4000, description="Шаблон сообщения")
    is_active: bool = Field(default=True, description="Активен ли шаблон")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Еженедельное напоминание",
                "message_template": "Привет! У нас есть новые материалы, которые могут быть полезны для вас.",
                "is_active": True,
            }
        }
    )


class AdminMessageTemplateUpdate(BaseModel):
    """Схема запроса обновления шаблона сообщения для PUT /api/v1/admin/message-templates/{id}."""

    name: Optional[str] = Field(None, min_length=3, max_length=255, description="Название шаблона")
    message_template: Optional[str] = Field(None, min_length=20, max_length=4000, description="Шаблон сообщения")
    is_active: Optional[bool] = Field(None, description="Активен ли шаблон")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Еженедельное напоминание",
                "message_template": "Привет! У нас есть новые материалы, которые могут быть полезны для вас.",
                "is_active": False,
            }
        }
    )
