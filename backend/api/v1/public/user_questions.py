"""Публичные эндпоинты для вопросов пользователей."""

from fastapi import APIRouter, status

from schemas.public.user_questions import (
    UserQuestionCreate,
    UserQuestionResponse,
)

router = APIRouter(prefix="/user-questions", tags=["Public User Questions"])


@router.post("/", response_model=UserQuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_user_question(
    request: UserQuestionCreate
) -> UserQuestionResponse:
    """
    Создание вопроса от пользователя.
    
    POST /api/v1/user-questions
    Позволяет пользователям Telegram задавать вопросы
    """
    pass
