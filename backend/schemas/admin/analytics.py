"""Административные схемы для аналитики."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AdminAnalyticsRequest(BaseModel):
    """Схема запроса аналитики для валидации параметров."""

    period: Optional[Literal["day", "week", "month", "year"]] = Field(default="month", description="Период аналитики")
    start_date: Optional[str] = Field(
        default=None, description="Начальная дата фильтрации (YYYY-MM-DD)", pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    end_date: Optional[str] = Field(
        default=None, description="Конечная дата фильтрации (YYYY-MM-DD)", pattern=r"^\d{4}-\d{2}-\d{2}$"
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"period": "month", "start_date": "2024-01-01", "end_date": "2024-01-31"}}
    )

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v):
        """Валидация формата даты YYYY-MM-DD."""
        if v is None:
            return v
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError("Дата должна быть в формате YYYY-MM-DD")

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v, info):
        """Валидация логики диапазона дат."""
        if v is None or info.data.get("start_date") is None:
            return v

        try:
            start_date = datetime.fromisoformat(info.data["start_date"])
            end_date = datetime.fromisoformat(v)

            if start_date > end_date:
                raise ValueError("Начальная дата не может быть больше конечной даты")

            return v
        except ValueError as e:
            if "не может быть больше" in str(e):
                raise
            raise ValueError("Ошибка в формате дат")


class AdminAnalyticsResponse(BaseModel):
    """Схема ответа аналитики для GET /api/v1/admin/analytics."""

    users: dict = Field(..., description="Статистика пользователей")
    content: dict = Field(..., description="Статистика контента")
    activities: dict = Field(..., description="Статистика активностей")
    questions: dict = Field(..., description="Статистика вопросов")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "users": {
                    "total": 1250,
                    "active_today": 45,
                    "active_week": 320,
                    "active_month": 890,
                },
                "content": {
                    "total_menu_items": 50,
                    "most_viewed": [
                        {
                            "id": 1,
                            "title": "Слуховые аппараты",
                            "view_count": 150,
                            "download_count": 45,
                            "average_rating": 4.5,
                        }
                    ],
                    "most_rated": [
                        {
                            "id": 2,
                            "title": "Типы слуховых аппаратов",
                            "average_rating": 4.8,
                            "rating_count": 25,
                        }
                    ],
                },
                "activities": {
                    "total_views": 5420,
                    "total_downloads": 890,
                    "total_ratings": 340,
                    "search_queries": [{"query": "слуховые аппараты", "count": 45}],
                },
                "questions": {"total": 150, "pending": 25, "answered": 125},
            }
        }
    )
