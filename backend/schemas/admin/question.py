"""Административные схемы для управления вопросами пользователей."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.models.enums import QuestionStatus


class AdminQuestionResponse(BaseModel):
    """Схема данных вопроса."""

    id: int = Field(..., description="ID вопроса")
    telegram_user_id: int = Field(..., description="ID пользователя Telegram")
    question_text: str = Field(..., description="Текст вопроса")
    answer_text: Optional[str] = Field(None, description="Текст ответа")
    status: QuestionStatus = Field(..., description="Статус вопроса")
    created_at: datetime = Field(..., description="Дата создания")
    answered_at: Optional[datetime] = Field(None, description="Дата ответа")

    model_config = ConfigDict(from_attributes=True)


class AdminQuestionListResponse(BaseModel):
    """Схема ответа списка вопросов для GET /api/v1/admin/user-questions."""

    items: List[AdminQuestionResponse] = Field(..., description="Список вопросов")
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Текущая страница")
    limit: int = Field(..., description="Лимит на странице")
    pages: int = Field(..., description="Общее количество страниц")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 1,
                        "telegram_user_id": 123456789,
                        "question_text": "Как выбрать слуховой аппарат для ребенка?",
                        "answer_text": None,
                        "status": "pending",
                        "created_at": "2024-01-15T10:00:00Z",
                        "answered_at": None,
                    }
                ],
                "total": 25,
                "page": 1,
                "limit": 20,
                "pages": 2,
            }
        }
    )


class AdminQuestionAnswer(BaseModel):
    """Схема запроса ответа на вопрос для PUT /api/v1/admin/user-questions/{id}."""

    answer_text: str = Field(
        ..., min_length=1, max_length=2000, description="Текст ответа"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "answer_text": "Для выбора слухового аппарата для ребенка необходимо..."
            }
        }
    )
