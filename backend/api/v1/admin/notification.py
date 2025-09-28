"""Административные эндпоинты для уведомлений."""

from fastapi import APIRouter, Depends, Query, status
from fastapi.security import HTTPBearer

from schemas.admin.notification import (
    AdminNotificationRequest,
    AdminNotificationResponse,
    AdminNotificationListResponse,
    AdminNotificationUpdate,
)

router = APIRouter(prefix="/admin/notifications", tags=["Admin Notifications"])
security = HTTPBearer()


@router.post("/", response_model=AdminNotificationResponse, status_code=status.HTTP_201_CREATED)
async def send_notification(
    request: AdminNotificationRequest,
    token: str = Depends(security)
) -> AdminNotificationResponse:
    """
    Отправка уведомления пользователю.
    
    POST /api/v1/admin/notifications
    Требует: Authorization: Bearer <token>
    """
    pass


@router.get("/", response_model=AdminNotificationListResponse, status_code=status.HTTP_200_OK)
async def get_notifications(
    page: int = Query(1, description="Номер страницы (по умолчанию 1)"),
    limit: int = Query(20, description="Количество записей на странице (по умолчанию 20)"),
    token: str = Depends(security)
) -> AdminNotificationListResponse:
    """
    Получение списка уведомлений.
    
    GET /api/v1/admin/notifications
    Требует: Authorization: Bearer <token>
    """
    pass


@router.get("/{id}", response_model=AdminNotificationResponse, status_code=status.HTTP_200_OK)
async def get_notification(
    id: int,
    token: str = Depends(security)
) -> AdminNotificationResponse:
    """
    Получение уведомления.
    
    GET /api/v1/admin/notifications/{id}
    Требует: Authorization: Bearer <token>
    """
    pass


@router.put("/{id}", response_model=AdminNotificationResponse, status_code=status.HTTP_200_OK)
async def update_notification(
    id: int,
    request: AdminNotificationUpdate,
    token: str = Depends(security)
) -> AdminNotificationResponse:
    """
    Обновление уведомления.
    
    PUT /api/v1/admin/notifications/{id}
    Требует: Authorization: Bearer <token>
    """
    pass


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    id: int,
    token: str = Depends(security)
) -> None:
    """
    Удаление уведомления.
    
    DELETE /api/v1/admin/notifications/{id}
    Требует: Authorization: Bearer <token>
    """
    pass
