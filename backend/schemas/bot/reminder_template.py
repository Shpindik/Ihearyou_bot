"""Pydantic схемы для шаблонов напоминаний."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BotReminderTemplateResponse(BaseModel):
    """Схема данных шаблона напоминания."""

    id: int = Field(..., description="ID шаблона")
    name: str = Field(..., description="Название шаблона")
    message_template: str = Field(..., description="Шаблон сообщения")
    is_active: bool = Field(..., description="Активен ли шаблон")
    inactive_days: int = Field(..., description="Количество дней без активности")

    model_config = ConfigDict(from_attributes=True)
