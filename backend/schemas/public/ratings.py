"""Публичные схемы для оценок материалов."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RatingRequest(BaseModel):
    """Схема запроса оценки материала для POST /api/v1/ratings."""

    telegram_user_id: int = Field(..., description="ID пользователя Telegram")
    menu_item_id: int = Field(..., description="ID пункта меню")
    rating: int = Field(..., ge=1, le=5, description="Оценка полезности материала (1-5)")

    model_config = ConfigDict(
        json_schema_extra={"example": {"telegram_user_id": 123456789, "menu_item_id": 1, "rating": 5}}
    )


class RatingResponse(BaseModel):
    """Схема ответа создания оценки для POST /api/v1/ratings."""

    success: bool = Field(True, description="Оценка успешно сохранена")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "success": True,
            }
        },
    )
