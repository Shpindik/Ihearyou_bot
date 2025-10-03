"""Публичные эндпоинты для оценки материалов."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.schemas.public.ratings import RatingRequest, RatingResponse
from backend.services.ratings import rating_service


router = APIRouter(prefix="/ratings")


@router.post(
    "/",
    response_model=RatingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Оценка полезности материала",
    description="Позволяет пользователям оценивать полезность материалов по пятиззвездочной системе",
    responses={
        201: {"description": "Оценка успешно поставлена"},
        400: {"description": "Ошибка валидации данных или некорректный рейтинг (1-5)"},
        404: {"description": "Материал не найден"},
        409: {"description": "Пользователь уже оценил этот материал"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def rate_material(request: RatingRequest, db: AsyncSession = Depends(get_session)) -> RatingResponse:
    """Оценка полезности материала.

    Позволяет пользователям оценивать полезность материалов от 1 до 5 звезд.
    Каждый пользователь может выставить только одну оценку для каждого материала.
    """
    return await rating_service.rate_material(request, db)
