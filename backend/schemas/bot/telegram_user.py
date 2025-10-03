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


class BotInactiveUserResponse(BaseModel):
    """Схема ответа для GET /api/v1/bot/telegram-user/inactive-users."""

    telegram_user_id: int = Field(..., description="ID пользователя в Telegram")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    username: Optional[str] = Field(None, description="Имя пользователя в Telegram")
    last_activity: Optional[str] = Field(None, description="Последняя активность")
    reminder_sent_at: Optional[str] = Field(None, description="Дата отправки последнего напоминания")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "telegram_user_id": 123456789,
                "first_name": "Иван",
                "last_name": "Иванов",
                "username": "ivan_ivanov",
                "last_activity": "2024-01-15T10:30:00Z",
                "reminder_sent_at": None,
            }
        },
    )


class BotReminderStatusResponse(BaseModel):
    """Схема ответа для POST /api/v1/bot/telegram-user/update-reminder-status."""

    success: str = Field(..., description="Статус успеха")
    message: str = Field(..., description="Сообщение о результате")
    reminder_sent_at: str = Field(..., description="Время отправки напоминания")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "success": "true",
                "message": "Статус напоминания обновлен для пользователя Иван",
                "reminder_sent_at": "2024-01-15T10:30:00.000000+00:00",
            }
        },
    )
