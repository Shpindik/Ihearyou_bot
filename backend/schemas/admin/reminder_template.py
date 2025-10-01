"""Pydantic схемы для шаблонов напоминаний."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class AdminReminderTemplateResponse(BaseModel):
    """Схема данных шаблона напоминания."""

    id: int = Field(..., description="ID шаблона")
    name: str = Field(..., description="Название шаблона")
    message_template: str = Field(..., description="Шаблон сообщения")
    is_active: bool = Field(..., description="Активен ли шаблон")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")
    inactive_days: int = Field(..., description="Количество дней без активности")

    model_config = ConfigDict(from_attributes=True)


class AdminReminderTemplateListResponse(BaseModel):
    """Схема ответа списка шаблонов напоминаний для GET /api/v1/admin/reminder-templates."""

    items: List[AdminReminderTemplateResponse] = Field(..., description="Список шаблонов")

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
                        "inactive_days": 10,
                    }
                ]
            }
        }
    )


class AdminReminderTemplateCreate(BaseModel):
    """Схема запроса создания шаблона напоминания для POST /api/v1/admin/reminder-templates."""

    name: str = Field(..., min_length=1, max_length=255, description="Название шаблона")
    message_template: str = Field(..., min_length=1, description="Шаблон сообщения")
    is_active: bool = Field(default=True, description="Активен ли шаблон")
    inactive_days: int = Field(default=10, description="Количество дней без активности")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Еженедельное напоминание",
                "message_template": "Привет! У нас есть новые материалы, которые могут быть полезны для вас.",
                "is_active": True,
                "inactive_days": 10,
            }
        }
    )

    @field_validator("*", mode="before")
    def check_not_empty(cls, value: str, field: ValidationInfo) -> str:
        """Проверка строк на пустоту."""
        if isinstance(value, str) and not value.strip():
            raise ValueError(f"Поле '{field.field_name}' не может быть пустым.")
        return value


class AdminReminderTemplateUpdate(BaseModel):
    """Схема запроса обновления шаблона напоминания для PUT /api/v1/admin/reminder-templates/{id}."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Название шаблона")
    message_template: Optional[str] = Field(None, min_length=1, description="Шаблон сообщения")
    is_active: Optional[bool] = Field(None, description="Активен ли шаблон")
    inactive_days: Optional[int] = Field(10, description="Количество дней без активности")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Еженедельное напоминание",
                "message_template": "Привет! У нас есть новые материалы, которые могут быть полезны для вас.",
                "is_active": False,
            }
        }
    )
