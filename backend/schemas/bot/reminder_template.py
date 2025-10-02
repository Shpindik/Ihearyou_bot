"""Bot API схемы для шаблонов напоминаний."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BotReminderTemplateResponse(BaseModel):
    """Схема ответа для Bot API с шаблоном напоминания."""

    id: int = Field(..., description="ID шаблона")
    name: str = Field(..., description="Название шаблона")
    message_template: str = Field(..., description="Шаблон сообщения")
    created_at: datetime = Field(..., description="Дата создания")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Еженедельное напоминание",
                "message_template": "Привет, {first_name}! У нас есть новые материалы для вас.",
                "created_at": "2024-01-01T12:00:00Z",
            }
        },
    )
