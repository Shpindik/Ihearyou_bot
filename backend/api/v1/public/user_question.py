"""Публичные эндпоинты для вопросов пользователей."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.core.exceptions import ValidationError
from backend.schemas.public.user_question import (
    UserQuestionCreate,
    UserQuestionResponse,
)
from backend.services.notification import notification_service
from backend.services.question import user_question_service


router = APIRouter(prefix="/user-questions", tags=["Public User Questions"])


@router.post(
    "/", response_model=UserQuestionResponse, status_code=status.HTTP_201_CREATED
)
async def create_user_question(request: UserQuestionCreate, db: AsyncSession = Depends(get_session)) -> UserQuestionResponse:
    """Создание вопроса от пользователя.

    POST /api/v1/user-questions
    Позволяет пользователям Telegram задавать вопросы
    """
    try:
        return await user_question_service.create_question(request, db)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка базы данных при создании вопроса"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера")


@router.get("/notifications/pending")
async def get_pending_notifications(limit: int = Query(50), db: AsyncSession = Depends(get_session)):
    try:
        return await notification_service.list_pending_for_bot(db, limit)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка базы данных при получении уведомлений")


@router.post("/notifications/{id}/sent", status_code=status.HTTP_204_NO_CONTENT)
async def mark_notification_sent(id: int, db: AsyncSession = Depends(get_session)):
    try:
        await notification_service.mark_sent(db, id)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка базы данных при обновлении уведомления")
