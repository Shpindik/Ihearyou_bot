"""Pydantic схемы для вопросов пользователей."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.models.enums import QuestionStatus


class UserQuestionCreate(BaseModel):
    """Схема создания вопроса пользователем для POST /api/v1/user-questions."""

    telegram_user_id: int = Field(..., description="ID пользователя Telegram")
    question_text: str = Field(..., min_length=10, max_length=2000, description="Текст вопроса")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "telegram_user_id": 123456789,
                "question_text": "Как правильно выбрать слуховой аппарат для ребенка 3 лет?",
            }
        }
    )


class UserQuestionResponse(BaseModel):
    """Схема ответа создания вопроса для POST /api/v1/user-questions."""

    question_text: str = Field(..., description="Текст вопроса")
    answer_text: Optional[str] = Field(None, description="Текст ответа")
    status: QuestionStatus = Field(..., description="Статус вопроса")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "question_text": "У меня есть ребенок с нарушением слуха. Как отличить глухого ребенка от ребенка, который просто не слушает?",
                "answer_text": None,
                "status": "pending",
            }
        },
    )
