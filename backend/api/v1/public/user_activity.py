"""Публичные эндпоинты для записи активности пользователей."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.schemas.public.user_activity import UserActivityRequest, UserActivityResponse
from backend.services.user_activity import user_activity_service


router = APIRouter(prefix="/user-activities")


@router.post(
    "/",
    response_model=UserActivityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Запись активности пользователя",
    description="Создает запись активности пользователя (просмотр, скачивание, поиск и т.д.)",
    responses={
        201: {"description": "Активность успешно записана"},
        400: {"description": "Ошибка валидации данных запроса"},
        404: {"description": "Пользователь не найден или пункт меню не найден"},
        422: {"description": "Ошибка валидации входных данных"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def record_user_activity(
    request: UserActivityRequest, db: AsyncSession = Depends(get_session)
) -> UserActivityResponse:
    """Запись активности пользователя.

    Используется ботом для записи просмотров, скачиваний и других действий.
    Автоматически проверяет существование пользователя и создает запись активности.
    """
    return await user_activity_service.record_activity(request, db)
