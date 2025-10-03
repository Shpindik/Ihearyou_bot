"""Модель пользователей Telegram."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.db import Base

from .enums import SubscriptionType


if TYPE_CHECKING:
    from .notification import Notification
    from .question import UserQuestion
    from .user_activity import UserActivity


class TelegramUser(Base):
    """Модель пользователей Telegram."""

    __tablename__ = "telegram_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    subscription_type: Mapped[Optional[SubscriptionType]] = mapped_column(String(20), nullable=True, index=True)
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    reminder_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Статистика
    activities_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    questions_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Связи
    activities: Mapped[List["UserActivity"]] = relationship(
        "UserActivity", back_populates="telegram_user", cascade="all, delete-orphan"
    )
    questions: Mapped[List["UserQuestion"]] = relationship(
        "UserQuestion", back_populates="telegram_user", cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="telegram_user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Строковое представление для отладки."""
        return f"<TelegramUser(id={self.id}, telegram_id={self.telegram_id}, first_name='{self.first_name}')>"

    def __str__(self) -> str:
        """Человекочитаемое строковое представление."""
        return f"User {self.first_name} {self.last_name or ''}"

    __table_args__ = (Index("ix_telegram_users_inactive_reminder", "last_activity", "reminder_sent_at"),)
