"""Административные эндпоинты для управления вопросами пользователей."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.core.exceptions import ValidationError
from backend.schemas.admin.question import (
    AdminQuestionAnswer,
    AdminQuestionListResponse,
    AdminQuestionResponse,
)
from backend.services.question import user_question_service
from backend.services.notification import notification_service
from sqlalchemy import select
from backend.models.telegram_user import TelegramUser


router = APIRouter(prefix="/admin/user-questions", tags=["Admin Questions"])
security = HTTPBearer()


@router.get(
    "/", response_model=AdminQuestionListResponse, status_code=status.HTTP_200_OK
)
async def get_user_questions(
    page: int = Query(1, description="Номер страницы (по умолчанию 1)"),
    limit: int = Query(
        20, description="Количество записей на странице (по умолчанию 20)"
    ),
    status: str = Query(None, description="Фильтр по статусу (pending, answered)"),
    token: str = Depends(security),
    db: AsyncSession = Depends(get_session),
) -> AdminQuestionListResponse:
    """Получение списка вопросов от пользователей.

    GET /api/v1/admin/user-questions
    Требует: Authorization: Bearer <token>
    """
    try:
        return await user_question_service.list_questions(db, page, limit, status)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка базы данных при получении вопросов"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера")


@router.put(
    "/{id}", response_model=AdminQuestionResponse, status_code=status.HTTP_200_OK
)
async def answer_question(
    id: int, request: AdminQuestionAnswer, token: str = Depends(security), db: AsyncSession = Depends(get_session)
) -> AdminQuestionResponse:
    """Ответ на вопрос пользователя.

    PUT /api/v1/admin/user-questions/{id}
    Требует: Authorization: Bearer <token>
    """
    try:
        resp = await user_question_service.answer_question(db, id, request)
        # Находим chat_id и ставим Celery-задачу на отправку
        q_user = (await db.execute(select(TelegramUser).where(TelegramUser.id == resp.telegram_user_id))).scalar_one()
        notification_service.enqueue_send_answer(
            telegram_chat_id=q_user.telegram_id,
            message=f"Мы ответили на ваш вопрос!\n\n{resp.answer_text}",
        )
        return resp
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка базы данных при обновлении вопроса"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера")
