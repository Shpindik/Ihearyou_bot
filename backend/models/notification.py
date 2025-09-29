"""Модель уведомлений."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.db import Base

from .enums import NotificationStatus


if TYPE_CHECKING:
    from .reminder_template import ReminderTemplate
    from .telegram_user import TelegramUser


class Notification(Base):
    """Модель уведомлений."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("telegram_users.id"), nullable=False, index=True
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        String(20), default=NotificationStatus.PENDING, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    template_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("reminder_templates.id"), nullable=True, index=True
    )

    # Связи
    telegram_user: Mapped["TelegramUser"] = relationship(
        "TelegramUser", back_populates="notifications"
    )
    template: Mapped[Optional["ReminderTemplate"]] = relationship(
        "ReminderTemplate", back_populates="notifications"
    )

    def __repr__(self) -> str:
        """Строковое представление для отладки."""
        return f"<Notification(id={self.id}, telegram_user_id={self.telegram_user_id}, status={self.status})>"

    def __str__(self) -> str:
        """Человекочитаемое строковое представление."""
        return f"Notification to telegram user {self.telegram_user_id} ({self.status})"
