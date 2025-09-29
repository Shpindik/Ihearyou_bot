"""Публичные схемы для поиска по материалам."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.models.enums import AccessLevel


class SearchItemResponse(BaseModel):
    """Схема элемента поиска для GET /api/v1/search."""

    id: int = Field(..., description="ID пункта меню")
    title: str = Field(..., description="Название пункта меню")
    description: Optional[str] = Field(None, description="Описание пункта меню")
    parent_id: Optional[int] = Field(None, description="ID родительского пункта")
    bot_message: Optional[str] = Field(None, description="Сообщение бота")
    is_active: bool = Field(..., description="Активен ли пункт")
    access_level: AccessLevel = Field(..., description="Уровень доступа")

    model_config = ConfigDict(from_attributes=True)


class SearchListResponse(BaseModel):
    """Схема ответа списка результатов поиска для GET /api/v1/search."""

    items: list[SearchItemResponse] = Field(
        ..., description="Список результатов поиска"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 1,
                        "title": "Слуховые аппараты",
                        "description": "Информация о слуховых аппаратах",
                        "parent_id": None,
                        "bot_message": "Выберите интересующий вас раздел:",
                        "is_active": True,
                        "access_level": "free",
                    }
                ]
            }
        }
    )
