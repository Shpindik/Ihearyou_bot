"""Pydantic схемы для пользователей Telegram."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.models.enums import SubscriptionType


class AdminTelegramUserResponse(BaseModel):
    """Схема данных пользователя Telegram для GET /api/v1/admin/telegram-users/{id}."""

    id: int = Field(..., description="ID пользователя в системе")
    telegram_id: int = Field(..., description="Telegram ID пользователя")
    username: Optional[str] = Field(None, description="Имя пользователя в Telegram")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    subscription_type: Optional[SubscriptionType] = Field(None, description="Тип подписки")
    last_activity: Optional[datetime] = Field(None, description="Последняя активность")
    reminder_sent_at: Optional[datetime] = Field(None, description="Дата отправки последнего напоминания")
    created_at: datetime = Field(..., description="Дата регистрации")
    activities_count: int = Field(..., description="Количество активностей")
    questions_count: int = Field(..., description="Количество вопросов")

    model_config = ConfigDict(from_attributes=True)


class AdminTelegramUserListResponse(BaseModel):
    """Схема ответа списка пользователей для GET /api/v1/admin/telegram-users."""

    items: list[AdminTelegramUserResponse] = Field(..., description="Список пользователей")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 1,
                        "telegram_id": 123456789,
                        "username": "ivan_ivanov",
                        "first_name": "Иван",
                        "last_name": "Иванов",
                        "subscription_type": "free",
                        "last_activity": "2024-01-15T10:30:00Z",
                        "created_at": "2024-01-01T12:00:00Z",
                    }
                ],
            }
        }
    )
