"""Сервис для работы с уведомлениями."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Notification, TelegramUser
from backend.models.enums import NotificationStatus
from backend.core.celery_app import celery_app


class NotificationService:
    """Сервис для работы с уведомлениями."""

    async def create_notification(self, db: AsyncSession, telegram_user_id: int, message: str) -> Notification:
        notification = Notification(
            telegram_user_id=telegram_user_id,
            message=message,
            status=NotificationStatus.PENDING,
        )
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification

    async def list_pending_for_bot(self, db: AsyncSession, limit: int = 50) -> List[dict]:
        """Возвращает список PENDING уведомлений с telegram chat id."""
        query = (
            select(Notification, TelegramUser.telegram_id)
            .join(TelegramUser, TelegramUser.id == Notification.telegram_user_id)
            .where(Notification.status == NotificationStatus.PENDING)
            .order_by(desc(Notification.created_at))
            .limit(limit)
        )
        result = await db.execute(query)
        rows = result.all()
        notifications = []
        for notif, chat_id in rows:
            notifications.append({
                "id": notif.id,
                "telegram_chat_id": chat_id,
                "message": notif.message,
            })
        return notifications

    async def mark_sent(self, db: AsyncSession, notification_id: int) -> None:
        result = await db.execute(select(Notification).where(Notification.id == notification_id))
        notif = result.scalar_one_or_none()
        if not notif:
            return
        notif.status = NotificationStatus.SENT
        notif.sent_at = datetime.now(timezone.utc)
        await db.commit()

    def enqueue_send_answer(self, telegram_chat_id: int, message: str) -> None:
        celery_app.send_task("backend.tasks.send_telegram_message", args=[telegram_chat_id, message])


notification_service = NotificationService()
