"""Административные эндпоинты для уведомлений."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.schemas.admin.notification import (
    AdminNotificationListResponse,
    AdminNotificationRequest,
    AdminNotificationResponse,
    AdminNotificationUpdate,
)
from backend.services.notification import notification_service


router = APIRouter(prefix="/admin/notifications", tags=["Admin Notifications"])
security = HTTPBearer()


@router.post(
    "/", response_model=AdminNotificationResponse, status_code=status.HTTP_201_CREATED
)
async def send_notification(
    request: AdminNotificationRequest, token: str = Depends(security), db: AsyncSession = Depends(get_session)
) -> AdminNotificationResponse:
    """Отправка уведомления пользователю.

    POST /api/v1/admin/notifications
    Требует: Authorization: Bearer <token>
    """
    try:
        notif = await notification_service.create_notification(
            db, telegram_user_id=request.telegram_user_id, message=request.message
        )
        return AdminNotificationResponse.model_validate(notif)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка базы данных при создании уведомления")


@router.get(
    "/", response_model=AdminNotificationListResponse, status_code=status.HTTP_200_OK
)
async def get_notifications(
    page: int = Query(1, description="Номер страницы (по умолчанию 1)"),
    limit: int = Query(
        20, description="Количество записей на странице (по умолчанию 20)"
    ),
    token: str = Depends(security),
    db: AsyncSession = Depends(get_session),
) -> AdminNotificationListResponse:
    """Получение списка уведомлений."""
    # Упростим: вернем последние PENDING как список (демо)
    try:
        items = await notification_service.list_pending_for_bot(db, limit=limit)
        total = len(items)
        return AdminNotificationListResponse(
            items=[
                AdminNotificationResponse(
                    id=i["id"], telegram_user_id=0, message=i["message"], status="pending", created_at=None, sent_at=None, template_id=None
                )
                for i in items
            ],
            total=total,
            page=1,
            limit=limit,
            pages=1,
        )
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка базы данных при получении уведомлений")


@router.get(
    "/{id}", response_model=AdminNotificationResponse, status_code=status.HTTP_200_OK
)
async def get_notification(
    id: int, token: str = Depends(security)
) -> AdminNotificationResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put(
    "/{id}", response_model=AdminNotificationResponse, status_code=status.HTTP_200_OK
)
async def update_notification(
    id: int, request: AdminNotificationUpdate, token: str = Depends(security)
) -> AdminNotificationResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(id: int, token: str = Depends(security)) -> None:
    raise HTTPException(status_code=501, detail="Not implemented")
