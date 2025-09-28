"""Схемы для webhook эндпоинтов."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TelegramWebhookRequest(BaseModel):
    """Схема запроса webhook от Telegram для POST /api/v1/webhook/telegram."""
    
    update_id: int = Field(..., description="ID обновления")
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
                        "is_bot": False,
                        "first_name": "Иван",
                        "last_name": "Иванов",
                        "username": "ivan_ivanov",
                        "language_code": "ru"
                    },
                    "chat": {
                        "id": 123456789,
                        "first_name": "Иван",
                        "last_name": "Иванов",
                        "username": "ivan_ivanov",
                        "type": "private"
                    },
                    "date": 1640995200,
                    "text": "/start"
                }
            }
        }
    )


class TelegramWebhookResponse(BaseModel):
    """Схема ответа webhook для POST /api/v1/webhook/telegram."""
    
    user: dict = Field(..., description="Данные пользователя")
    message_processed: bool = Field(..., description="Сообщение обработано")
    user_created: bool = Field(..., description="Пользователь создан")
    user_updated: bool = Field(..., description="Пользователь обновлен")
    
    model_config = ConfigDict(
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
                    "created_at": "2024-01-01T12:00:00Z"
                },
                "message_processed": True,
                "user_created": True,
                "user_updated": True
            }
        }
    )
