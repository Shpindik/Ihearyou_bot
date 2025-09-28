"""Публичные эндпоинты для оценки материалов."""

from fastapi import APIRouter, status

from schemas.public.ratings import (
    RatingRequest,
    RatingResponse,
)

router = APIRouter(prefix="/ratings", tags=["Public Ratings"])


@router.post("/", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def rate_material(
    request: RatingRequest
) -> RatingResponse:
    """
    Оценка полезности материала.
    
    POST /api/v1/ratings
    Позволяет пользователям оценивать полезность материалов (1-5 звезд)
    """
    pass
