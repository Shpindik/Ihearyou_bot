"""Административные эндпоинты для уведомлений."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.core.dependencies import AdminOnly, ModeratorOrAdmin
from backend.schemas.admin.notification import (
    AdminNotificationListResponse,
    AdminNotificationRequest,
    AdminNotificationResponse,
    AdminNotificationUpdate,
)
from backend.services.notification import notification_service


router = APIRouter(prefix="/notifications", tags=["Admin Notifications"])


@router.post(
    "/",
    response_model=AdminNotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Отправка уведомления пользователю (админ)",
    description="Отправляет уведомление конкретному пользователю через Telegram",
    responses={
        201: {"description": "Уведомление успешно отправлено"},
        400: {"description": "Ошибка валидации данных"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Пользователь не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def send_notification(
    request: AdminNotificationRequest,
    current_admin: ModeratorOrAdmin,
    db: AsyncSession = Depends(get_session),
) -> AdminNotificationResponse:
    """Отправка уведомления пользователю.

    Требует авторизации с ролью модератора или администратора.
    Отправляет уведомление конкретному пользователю Telegram.
    """
    return await notification_service.send_admin_notification(db=db, request=request)


@router.get(
    "/",
    response_model=AdminNotificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="Подсчет отправленных уведомлений (админ)",
    description="Возвращает статистику отправленных уведомлений с фильтрацией по датам",
    responses={
        200: {"description": "Статистика уведомлений успешно получена"},
        400: {"description": "Ошибка валидации параметров запроса"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_notifications(
    current_admin: ModeratorOrAdmin,
    days_ago: Optional[int] = Query(None, description="Фильтр по дням назад"),
    db: AsyncSession = Depends(get_session),
) -> AdminNotificationListResponse:
    """Получение статистики уведомлений для администраторов.

    Требует авторизации с ролью модератора или администратора.
    Возвращает статистику отправленных уведомлений с возможностью фильтрации по периодам.
    """
    return await notification_service.get_admin_notifications(db=db, days_ago=days_ago)


@router.put(
    "/{id}",
    response_model=AdminNotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновление статуса уведомления (админ)",
    description="Обновляет статус уведомления в системе",
    responses={
        200: {"description": "Статус уведомления успешно обновлен"},
        400: {"description": "Ошибка валидации данных"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Уведомление не найдено"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def update_notification(
    id: int,
    request: AdminNotificationUpdate,
    current_admin: AdminOnly,
    db: AsyncSession = Depends(get_session),
) -> AdminNotificationResponse:
    """Обновление статуса уведомления.

    Требует авторизации с ролью администратора.
    Позволяет изменить статус уведомления при необходимости.
    """
    return await notification_service.update_admin_notification(db=db, notification_id=id, request=request)


@router.get(
    "/statistics",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Получение статистики уведомлений (админ)",
    description="Возвращает детальную статистику по всем уведомлениям системы",
    responses={
        200: {"description": "Статистика уведомлений успешно получена"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_notification_statistics(
    current_admin: AdminOnly,
    db: AsyncSession = Depends(get_session),
) -> dict:
    """Получение детальной статистики уведомлений.

    Требует авторизации с ролью администратора.
    Возвращает полную статистику по всем уведомлениям в системе.
    """
    return await notification_service.get_notification_statistics(db=db)
