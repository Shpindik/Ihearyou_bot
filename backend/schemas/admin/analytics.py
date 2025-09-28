"""Административные схемы для аналитики."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field, ConfigDict


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
                    "active_month": 890
                },
                "content": {
                    "total_menu_items": 50,
                    "most_viewed": [
                        {
                            "id": 1,
                            "title": "Слуховые аппараты",
                            "view_count": 150,
                            "download_count": 45,
                            "average_rating": 4.5
                        }
                    ],
                    "most_rated": [
                        {
                            "id": 2,
                            "title": "Типы слуховых аппаратов",
                            "average_rating": 4.8,
                            "rating_count": 25
                        }
                    ]
                },
                "activities": {
                    "total_views": 5420,
                    "total_downloads": 890,
                    "total_ratings": 340,
                    "search_queries": [
                        {
                            "query": "слуховые аппараты",
                            "count": 45
                        }
                    ]
                },
                "questions": {
                    "total": 150,
                    "pending": 25,
                    "answered": 125
                }
            }
        }
    )
