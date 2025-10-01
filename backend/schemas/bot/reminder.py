"""Схемы для Bot API эндпоинтов."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class InactiveUserResponse(BaseModel):
    """Схема данных пользователя Telegram для GET GET /api/v1/bot/reminders/inactive_users."""

    id: int = Field(..., description="ID пользователя в системе")
    telegram_id: int = Field(..., description="Telegram ID пользователя")
    username: Optional[str] = Field(None, description="Имя пользователя в Telegram")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    last_activity: Optional[datetime] = Field(None, description="Последняя активность")

    model_config = ConfigDict(from_attributes=True)


class InactiveListUserResponse(BaseModel):
    """Схема ответа неактивных пользователей для GET /api/v1/bot/reminders/inactive_users."""

    users: List[InactiveUserResponse] = Field([], description="Список пользователей")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "users": [
                    {
                        "id": 1,
                        "telegram_id": 123456789,
                        "username": "ivan_ivanov",
                        "first_name": "Иван",
                        "last_name": "Иванов",
                        "last_activity": "2024-01-15T10:30:00Z",
                    }
                ]
            }
        }
    )
