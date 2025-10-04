"""Реальный сервис уведомлений с интеграцией Telegram Bot API."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import notification_crud, telegram_user_crud
from backend.schemas.admin.notification import (
    AdminNotificationListResponse,
    AdminNotificationRequest,
    AdminNotificationResponse,
    AdminNotificationUpdate,
)
from backend.services.message_template import message_template_service
from backend.validators.notification import notification_validator


class NotificationService:
    """Сервис управления уведомлениями в БД (отправка через бот в scheduler_tasks.py)."""

    def __init__(self):
        """Инициализация сервиса управления уведомлениями."""
        self.validator = notification_validator

    async def find_inactive_users(self, db: AsyncSession, inactive_days: int = 10) -> List:
        """Найти неактивных пользователей."""
        return await telegram_user_crud.get_inactive_users(db, inactive_days)

    async def create_reminder_notifications(self, db: AsyncSession, users: List) -> int:
        """Создать напоминания для пользователей с использованием активных шаблонов."""
        # Получаем активный шаблон по умолчанию
        template = await message_template_service.get_default_template(db)

        count = 0
        for user in users:
            if template:
                # Используем шаблон с персонализацией
                message = message_template_service.personalize_message(template.message_template, user.first_name)
                await notification_crud.create_notification(
                    db=db, telegram_user_id=user.id, message=message, template_id=template.id
                )
            else:
                # Fallback сообщение если шаблонов нет
                message = f"Привет, {user.first_name}! Мы по вам соскучились! 🥰"
                await notification_crud.create_notification(db=db, telegram_user_id=user.id, message=message)
            count += 1
        return count

    async def send_pending_notifications(self, db: AsyncSession) -> dict:
        """Получить ожидающие уведомления для отправки ботом.

        ВНИМАНИЕ: Прямая отправка через Telegram перенесена в бот!
        Этот сервис только управляет данными в БД.
        """
        notifications = await notification_crud.get_pending_notifications(db)
        return {"total": len(notifications), "pending_notifications": notifications}

    async def send_admin_notification(
        self, db: AsyncSession, request: AdminNotificationRequest
    ) -> AdminNotificationResponse:
        """Отправить админское уведомление пользователю."""
        user = await telegram_user_crud.get_by_telegram_id(db, request.telegram_user_id)
        self.validator.validate_user_exists_for_id(user, request.telegram_user_id)

        notification = await notification_crud.create_notification(
            db=db,
            telegram_user_id=user.id,
            message=request.message,
        )

        print(f"📝 Админское уведомление создано в БД для пользователя {user.telegram_id}")
        await telegram_user_crud.update_reminder_sent_status(db, telegram_user_id=user.id)

        return AdminNotificationResponse.model_validate(notification.__dict__)

    async def get_admin_notifications(
        self, db: AsyncSession, days_ago: Optional[int] = None
    ) -> AdminNotificationListResponse:
        """Получить статистику уведомлений для админов."""
        start_date = None
        if days_ago:
            start_date = datetime.now(timezone.utc) - timedelta(days=days_ago)

        stats = await notification_crud.get_notification_statistics(db, start_date)

        # Получаем список уведомлений для admin панели
        notifications = await notification_crud.get_admin_notifications(db, start_date)

        return AdminNotificationListResponse(
            items=notifications,
            total=stats["total"],
            page=1,
            limit=100,  # В текущей реализации все уведомления
            pages=1,
        )

    async def update_admin_notification(
        self, db: AsyncSession, notification_id: int, request: AdminNotificationUpdate
    ) -> AdminNotificationResponse:
        """Обновить админское уведомление."""
        notification = await notification_crud.get(db, notification_id)
        self.validator.validate_notification_exists_for_id(notification, notification_id)

        # Обновляем статус
        if request.status == "sent":
            await notification_crud.mark_as_sent(db, notification_id)
        elif request.status == "failed":
            await notification_crud.mark_as_failed(db, notification_id)

        updated_notification = await notification_crud.get(db, notification_id)
        return AdminNotificationResponse.model_validate(updated_notification.__dict__)

    async def delete_admin_notification(self, db: AsyncSession, notification_id: int) -> None:
        """Удалить админское уведомление."""
        notification = await notification_crud.get(db, notification_id)
        self.validator.validate_notification_exists_for_id(notification, notification_id)

        await notification_crud.delete(db, notification_id)

    async def get_notification_statistics(self, db: AsyncSession) -> dict:
        """Получить общую статистику уведомлений."""
        stats = await notification_crud.get_notification_statistics(db)
        return stats


notification_service = NotificationService()
