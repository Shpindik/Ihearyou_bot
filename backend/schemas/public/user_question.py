"""Pydantic схемы для вопросов пользователей."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from models.enums import QuestionStatus


class UserQuestionCreate(BaseModel):
    """Схема создания вопроса пользователем для POST /api/v1/user-questions."""
    
    telegram_user_id: int = Field(..., description="ID пользователя Telegram")
    question_text: str = Field(..., min_length=1, max_length=2000, description="Текст вопроса")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "telegram_user_id": 123456789,
                "question_text": "Как правильно выбрать слуховой аппарат для ребенка 3 лет?"
            }
        }
    )


class UserQuestionResponse(BaseModel):
    """Схема ответа создания вопроса для POST /api/v1/user-questions."""
    
    id: int = Field(..., description="ID вопроса")
    telegram_user_id: int = Field(..., description="ID пользователя Telegram")
    question_text: str = Field(..., description="Текст вопроса")
    answer_text: Optional[str] = Field(None, description="Текст ответа")
    status: QuestionStatus = Field(..., description="Статус вопроса")
    answered_at: Optional[datetime] = Field(None, description="Дата ответа")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 456,
                "telegram_user_id": 123456789,
                "question_text": "Как выбрать слуховой аппарат для ребенка?",
                "answer_text": None,
                "status": "pending",
                "answered_at": None
            }
        }
    )


