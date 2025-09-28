"""Административные эндпоинты для управления вопросами пользователей."""

from fastapi import APIRouter, Depends, Query, status
from fastapi.security import HTTPBearer

from schemas.admin.questions import (
    AdminQuestionResponse,
    AdminQuestionListResponse,
    AdminQuestionAnswer,
)

router = APIRouter(prefix="/admin/user-questions", tags=["Admin Questions"])
security = HTTPBearer()


@router.get("/", response_model=AdminQuestionListResponse, status_code=status.HTTP_200_OK)
async def get_user_questions(
    page: int = Query(1, description="Номер страницы (по умолчанию 1)"),
    limit: int = Query(20, description="Количество записей на странице (по умолчанию 20)"),
    status: str = Query(None, description="Фильтр по статусу (pending, answered)"),
    token: str = Depends(security)
) -> AdminQuestionListResponse:
    """
    Получение списка вопросов от пользователей.
    
    GET /api/v1/admin/user-questions
    Требует: Authorization: Bearer <token>
    """
    pass


@router.put("/{id}", response_model=AdminQuestionResponse, status_code=status.HTTP_200_OK)
async def answer_question(
    id: int,
    request: AdminQuestionAnswer,
    token: str = Depends(security)
) -> AdminQuestionResponse:
    """
    Ответ на вопрос пользователя.
    
    PUT /api/v1/admin/user-questions/{id}
    Требует: Authorization: Bearer <token>
    """
    pass
