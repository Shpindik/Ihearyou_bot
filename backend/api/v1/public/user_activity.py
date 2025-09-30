"""Публичные эндпоинты для записи активности пользователей."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.core.exceptions import ValidationError
from backend.schemas.public.user_activity import UserActivityRequest, UserActivityResponse
from backend.services.user_activity import user_activity_service


router = APIRouter(prefix="/user-activities", tags=["Public User Activities"])


@router.post(
    "/",
    response_model=UserActivityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Запись активности пользователя",
    description="Создает запись активности пользователя (просмотр, скачивание, поиск и т.д.)",
    responses={
        201: {"description": "Активность успешно записана"},
        400: {"description": "Ошибка валидации данных запроса"},
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
    try:
        return await user_activity_service.record_activity(request, db)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка базы данных при записи активности"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера")
