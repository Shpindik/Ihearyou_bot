"""Публичные эндпоинты для записи активности пользователей."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_session
from crud import user_crud, activity_crud
from schemas.public.user_activities import (
    UserActivityRequest,
    UserActivityResponse,
)

router = APIRouter(prefix="/user-activities", tags=["Public User Activities"])


@router.post("/", response_model=UserActivityResponse, status_code=status.HTTP_201_CREATED)
async def record_user_activity(
    request: UserActivityRequest,
    db: AsyncSession = Depends(get_session)
) -> UserActivityResponse:
    """
    Запись активности пользователя.
    
    POST /api/v1/user-activities
    Используется ботом для записи просмотров, скачиваний и других действий
    """
    # Получаем пользователя
    user = await user_crud.get_by_telegram_id(db, request.telegram_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Создаем запись активности
    activity = await activity_crud.create_activity(
        db=db,
        telegram_user_id=user.id,
        menu_item_id=request.menu_item_id,
        activity_type=request.activity_type,
        search_query=request.search_query
    )
    
    return UserActivityResponse(
        id=activity.id,
        telegram_user_id=activity.telegram_user_id,
        menu_item_id=activity.menu_item_id,
        activity_type=activity.activity_type,
        rating=activity.rating,
        search_query=activity.search_query
    )
