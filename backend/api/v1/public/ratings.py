"""Публичные эндпоинты для оценки материалов."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.public.ratings import RatingRequest, RatingResponse
from backend.core.db import get_session
from backend.core.exceptions import IHearYouException, ValidationError
from backend.services.user_activity import user_activity_service
from backend.models.enums import ActivityType


router = APIRouter(prefix="/ratings", tags=["Public Ratings"])


@router.post("/", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def rate_material(request: RatingRequest, db: AsyncSession = Depends(get_session)) -> RatingResponse:
    """Оценка полезности материала.

    POST /api/v1/ratings
    Позволяет пользователям оценивать полезность материалов (1-5 звезд)
    """
    try:
        # Записываем активность с типом RATING через общий сервис активностей
        activity = await user_activity_service.record_activity(
            request=type("UAReq", (), {
                "telegram_user_id": request.telegram_user_id,
                "menu_item_id": request.menu_item_id,
                "activity_type": ActivityType.RATING,
                "search_query": None,
                "rating": request.rating,
            })(),
            db=db,
        )

        # Приводим к схеме ответа рейтингов
        return RatingResponse(
            id=activity.id,
            telegram_user_id=activity.telegram_user_id,
            menu_item_id=activity.menu_item_id,
            activity_type=activity.activity_type,
            rating=request.rating,
            search_query=activity.search_query,
        )
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка базы данных при записи оценки"
        )
    except IHearYouException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера")
