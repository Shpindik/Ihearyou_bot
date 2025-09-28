"""Модель пользователей Telegram."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from .enums import SubscriptionType

if TYPE_CHECKING:
    from .user_activity import UserActivity
    from .question import UserQuestion
    from .notification import Notification


class TelegramUser(Base):
    """Модель пользователей Telegram."""
    
    __tablename__ = "telegram_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    subscription_type: Mapped[Optional[SubscriptionType]] = mapped_column(String(20), nullable=True, index=True)
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reminder_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

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
        return f"<TelegramUser(id={self.id}, telegram_id={self.telegram_id}, first_name='{self.first_name}')>"

    def __str__(self) -> str:
        return f"User {self.first_name} {self.last_name or ''}"