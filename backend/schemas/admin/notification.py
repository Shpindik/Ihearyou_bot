"""Административные схемы для уведомлений."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.models.enums import NotificationStatus


class AdminNotificationRequest(BaseModel):
    """Схема запроса отправки уведомления для POST /api/v1/admin/notifications."""

    telegram_user_id: int = Field(..., description="ID пользователя Telegram")
    message: str = Field(..., min_length=10, max_length=4000, description="Текст уведомления")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "telegram_user_id": 123456789,
                "message": "Напоминание: не забудьте проверить новые материалы!",
            }
        }
    )


class AdminNotificationResponse(BaseModel):
    """Схема данных уведомления."""

    id: int = Field(..., description="ID уведомления")
    telegram_user_id: int = Field(..., description="ID пользователя Telegram")
    message: str = Field(..., description="Текст уведомления")
    status: NotificationStatus = Field(..., description="Статус уведомления")
    created_at: datetime = Field(..., description="Дата создания")
    sent_at: Optional[datetime] = Field(None, description="Дата отправки")
    template_id: Optional[int] = Field(None, description="ID шаблона")

    model_config = ConfigDict(from_attributes=True)


class AdminNotificationListResponse(BaseModel):
    """Схема ответа списка уведомлений для GET /api/v1/admin/notifications."""

    items: List[AdminNotificationResponse] = Field(..., description="Список уведомлений")
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Текущая страница")
    limit: int = Field(..., description="Лимит на странице")
    pages: int = Field(..., description="Общее количество страниц")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 789,
                        "telegram_user_id": 123456789,
                        "message": "Напоминание: не забудьте проверить новые материалы!",
                        "status": "sent",
                        "created_at": "2024-01-15T20:00:00Z",
                        "sent_at": "2024-01-15T20:00:00Z",
                        "template_id": 1,
                    }
                ],
                "total": 50,
                "page": 1,
                "limit": 20,
                "pages": 3,
            }
        }
    )


class AdminNotificationUpdate(BaseModel):
    """Схема запроса обновления уведомления для PUT /api/v1/admin/notifications/{id}."""

    status: Optional[NotificationStatus] = Field(None, description="Статус уведомления")
    sent_at: Optional[datetime] = Field(None, description="Дата отправки")

    model_config = ConfigDict(json_schema_extra={"example": {"status": "sent", "sent_at": "2024-01-15T20:00:00Z"}})
