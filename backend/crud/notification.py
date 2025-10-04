"""CRUD операции для уведомлений - упрощенная MVP версия."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Notification
from backend.models.enums import NotificationStatus

from .base import BaseCRUD


class NotificationCRUD(BaseCRUD[Notification, dict, dict]):
    """CRUD операции для уведомлений."""

    def __init__(self):
        """Инициализация CRUD для уведомлений."""
        super().__init__(Notification)

    async def get_pending_notifications(self, db: AsyncSession) -> List[Notification]:
        """Получить ожидающие уведомления."""
        query = (
            select(Notification)
            .where(Notification.status == NotificationStatus.PENDING)
            .order_by(Notification.created_at.asc())
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def mark_as_sent(self, db: AsyncSession, notification_id: int) -> bool:
        """Отметить уведомление как отправленное."""
        await db.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(status=NotificationStatus.SENT, sent_at=datetime.now(timezone.utc))
        )
        return True

    async def mark_as_failed(self, db: AsyncSession, notification_id: int) -> bool:
        """Отметить уведомление как неудачное."""
        await db.execute(
            update(Notification).where(Notification.id == notification_id).values(status=NotificationStatus.FAILED)
        )
        return True

    async def get_admin_notifications(self, db: AsyncSession, start_date=None) -> List[Notification]:
        """Получить все уведомления для админ панели."""
        query = select(Notification).order_by(Notification.created_at.desc())

        if start_date:
            query = query.where(Notification.created_at >= start_date)

        result = await db.execute(query)
        return result.scalars().all()

    async def create_notification(
        self, db: AsyncSession, telegram_user_id: int, message: str, template_id: int = None
    ) -> Notification:
        """Создать уведомление."""
        notification_data = {
            "telegram_user_id": telegram_user_id,
            "message": message,
            "status": NotificationStatus.PENDING,
            "template_id": template_id,
        }

        db_obj = self.model(**notification_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, notification_id: int) -> bool:
        """Удалить уведомление по ID."""
        notification = await self.remove(db, id=notification_id)
        return notification is not None

    async def get_notification_statistics(self, db: AsyncSession, start_date=None) -> dict:
        """Получить статистику уведомлений."""
        query = select(Notification)
        if start_date:
            query = query.where(Notification.created_at >= start_date)

        result = await db.execute(query)
        notifications = result.scalars().all()

        total = len(notifications)
        sent = sum(1 for n in notifications if n.status == NotificationStatus.SENT)
        failed = sum(1 for n in notifications if n.status == NotificationStatus.FAILED)
        pending = sum(1 for n in notifications if n.status == NotificationStatus.PENDING)

        success_rate = round((sent / total * 100) if total > 0 else 0, 2)

        return {
            "total": total,
            "sent": sent,
            "failed": failed,
            "pending": pending,
            "success_rate": success_rate,
        }


notification_crud = NotificationCRUD()
