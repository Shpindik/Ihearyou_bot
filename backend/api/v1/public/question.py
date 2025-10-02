"""Публичные эндпоинты для вопросов пользователей."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.schemas.public.question import UserQuestionCreate, UserQuestionResponse
from backend.services.question import user_question_service


router = APIRouter(prefix="/user-questions", tags=["Public User Questions"])


@router.post(
    "/",
    response_model=UserQuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание вопроса от пользователя",
    description="Позволяет пользователям Telegram задавать вопросы и рассчитывать автоматическое обновление счетчиков",
    responses={
        201: {"description": "Вопрос успешно создан"},
        400: {"description": "Ошибка валидации данных или пустой текст вопроса"},
        404: {"description": "Пользователь не найден"},
        422: {"description": "Содержимое содержит недопустимые символы"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def create_user_question(
    request: UserQuestionCreate, db: AsyncSession = Depends(get_session)
) -> UserQuestionResponse:
    """Создание вопроса от пользователя.

    Позволяет пользователям Telegram задавать вопросы.
    Требует наличия пользователя в системе (регистрация через Bot API).
    """
    return await user_question_service.create_user_question(request, db)
