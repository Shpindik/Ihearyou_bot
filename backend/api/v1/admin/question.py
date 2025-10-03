"""Административные эндпоинты для управления вопросами пользователей."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.core.dependencies import ModeratorOrAdmin
from backend.schemas.admin.question import AdminQuestionAnswer, AdminQuestionListResponse, AdminQuestionResponse
from backend.services.question import user_question_service


router = APIRouter(prefix="/user-questions", tags=["Admin Questions"])


@router.get(
    "/",
    response_model=AdminQuestionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение списка вопросов от пользователей",
    description="Возвращает пагинированный список вопросов с возможностью фильтрации для администраторов и модераторов",
    responses={
        200: {"description": "Список вопросов успешно получен"},
        400: {"description": "Ошибка валидации параметров запроса"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_user_questions(
    current_admin: ModeratorOrAdmin,
    page: int = Query(1, description="Номер страницы (по умолчанию 1)"),
    limit: int = Query(20, description="Количество записей на странице (по умолчанию 20)"),
    status: str = Query(None, description="Фильтр по статусу (pending, answered)"),
    db: AsyncSession = Depends(get_session),
) -> AdminQuestionListResponse:
    """Получение списка вопросов от пользователей.

    Требует авторизации с ролью модератора или администратора.
    Возвращает пагинированный список с возможностью фильтрации по статусу.
    """
    return await user_question_service.get_admin_questions(db=db, page=page, limit=limit, status=status)


@router.put(
    "/{id}",
    response_model=AdminQuestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Ответ на вопрос пользователя",
    description="Позволяет администраторам и модераторам отвечать на вопросы пользователей",
    responses={
        200: {"description": "Ответ успешно добавлен к вопросу"},
        400: {"description": "Ошибка валидации данных ответа"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Вопрос не найден"},
        422: {"description": "Содержимое ответа содержит недопустимые символы"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def answer_question(
    id: int,
    request: AdminQuestionAnswer,
    current_admin: ModeratorOrAdmin,
    db: AsyncSession = Depends(get_session),
) -> AdminQuestionResponse:
    """Ответ на вопрос пользователя.

    Требует авторизации с ролью модератора или администратора.
    Позволяет отвечать на вопросы пользователей и обновляет статус вопроса.
    """
    return await user_question_service.answer_question(
        db=db, question_id=id, request=request, admin_user_id=current_admin.id
    )
