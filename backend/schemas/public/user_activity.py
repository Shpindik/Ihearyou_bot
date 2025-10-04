"""Публичные схемы для активности пользователей."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.models.enums import ActivityType


class UserActivityRequest(BaseModel):
    """Схема запроса записи активности пользователя для POST /api/v1/user-activities."""

    telegram_user_id: int = Field(..., description="ID пользователя Telegram")
    menu_item_id: Optional[int] = Field(None, description="ID пункта меню")
    activity_type: ActivityType = Field(..., description="Тип активности")
    search_query: Optional[str] = Field(None, description="Поисковый запрос")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Оценка материала (1-5)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "telegram_user_id": 123456789,
                "menu_item_id": 1,
                "activity_type": "rating",
                "search_query": None,
                "rating": 5,
            }
        }
    )


class UserActivityResponse(BaseModel):
    """Схема ответа записи активности для POST /api/v1/user-activities."""

    menu_item_id: Optional[int] = Field(None, description="ID пункта меню")
    activity_type: ActivityType = Field(..., description="Тип активности")
    rating: Optional[int] = Field(None, description="Оценка полезности материала")
    search_query: Optional[str] = Field(None, description="Поисковый запрос")
    message: str = Field(..., description="Сообщение об успешной операции")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "menu_item_id": 1,
                "activity_type": "view",
                "rating": None,
                "search_query": None,
                "message": "Активность успешно записана",
            }
        },
    )
