"""Схемы для Bot API эндпоинтов."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TelegramUserRequest(BaseModel):
    """Схема запроса регистрации пользователя от бота для POST /api/v1/bot/telegram-user/register."""

    update_id: int = Field(..., gt=0, description="ID обновления")
    message: Optional[dict] = Field(None, description="Сообщение от пользователя")
    callback_query: Optional[dict] = Field(None, description="Callback запрос")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "update_id": 123456789,
                "message": {
                    "message_id": 1,
                    "from": {
                        "id": 123456789,
                        "first_name": "Иван",
                        "last_name": "Иванов",
                        "username": "ivan_ivanov",
                    },
                    "chat": {
                        "id": 123456789,
                        "type": "private",
                    },
                    "date": 1640995200,
                    "text": "/start",
                },
            }
        }
    )


class TelegramUserResponse(BaseModel):
    """Схема ответа регистрации пользователя для POST /api/v1/bot/telegram-user/register."""

    user: dict = Field(..., description="Данные пользователя")
    message_processed: bool = Field(..., description="Сообщение обработано")
    user_created: bool = Field(..., description="Пользователь создан")
    user_updated: bool = Field(..., description="Пользователь обновлен")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "user": {
                    "id": 1,
                    "telegram_id": 123456789,
                    "username": "ivan_ivanov",
                    "first_name": "Иван",
                    "last_name": "Иванов",
                    "subscription_type": "free",
                    "last_activity": "2024-01-15T10:30:00Z",
                    "reminder_sent_at": None,
                    "created_at": "2024-01-01T12:00:00Z",
                },
                "message_processed": True,
                "user_created": True,
                "user_updated": True,
            }
        },
    )
