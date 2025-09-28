"""Публичные схемы для оценок материалов."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from models.enums import ActivityType


class RatingRequest(BaseModel):
    """Схема запроса оценки материала для POST /api/v1/ratings."""
    
    telegram_user_id: int = Field(..., description="ID пользователя Telegram")
    menu_item_id: int = Field(..., description="ID пункта меню")
    rating: int = Field(..., ge=1, le=5, description="Оценка полезности материала (1-5)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "telegram_user_id": 123456789,
                "menu_item_id": 1,
                "rating": 5
            }
        }
    )


class RatingResponse(BaseModel):
    """Схема ответа создания оценки для POST /api/v1/ratings."""
    
    id: int = Field(..., description="ID созданной оценки")
    telegram_user_id: int = Field(..., description="ID пользователя Telegram")
    menu_item_id: int = Field(..., description="ID пункта меню")
    activity_type: ActivityType = Field(..., description="Тип активности")
    rating: int = Field(..., description="Оценка полезности материала")
    search_query: Optional[str] = Field(None, description="Поисковый запрос")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 789,
                "telegram_user_id": 123456789,
                "menu_item_id": 1,
                "activity_type": "rating",
                "rating": 5,
                "search_query": None
            }
        }
    )
