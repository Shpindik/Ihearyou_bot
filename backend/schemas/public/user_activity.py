"""Публичные схемы для активности пользователей."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from models.enums import ActivityType


class UserActivityRequest(BaseModel):
    """Схема запроса записи активности пользователя для POST /api/v1/user-activities."""
    
    telegram_user_id: int = Field(..., description="ID пользователя Telegram")
    menu_item_id: int = Field(..., description="ID пункта меню")
    activity_type: ActivityType = Field(..., description="Тип активности")
    search_query: Optional[str] = Field(None, description="Поисковый запрос")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "telegram_user_id": 123456789,
                "menu_item_id": 1,
                "activity_type": "view",
                "search_query": "слуховые аппараты"
            }
        }
    )


class UserActivityResponse(BaseModel):
    """Схема ответа записи активности для POST /api/v1/user-activities."""
    
    id: int = Field(..., description="ID активности")
    telegram_user_id: int = Field(..., description="ID пользователя Telegram")
    menu_item_id: int = Field(..., description="ID пункта меню")
    activity_type: ActivityType = Field(..., description="Тип активности")
    rating: Optional[int] = Field(None, description="Оценка полезности материала")
    search_query: Optional[str] = Field(None, description="Поисковый запрос")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 123,
                "telegram_user_id": 123456789,
                "menu_item_id": 1,
                "activity_type": "view",
                "rating": None,
                "search_query": "слуховые аппараты"
            }
        }
    )
