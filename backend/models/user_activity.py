"""Модель аналитики и активности."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from .enums import ActivityType

if TYPE_CHECKING:
    from .menu import MenuItem


class UserActivity(Base):
    """Модель активности пользователей."""
    
    __tablename__ = "user_activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("telegram_users.id"), nullable=False, index=True
    )
    activity_type: Mapped[ActivityType] = mapped_column(
        String(50), nullable=False
    )
    menu_item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("menu_items.id"), nullable=False, index=True
    )
    search_query: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Связи
    telegram_user: Mapped["TelegramUser"] = relationship("TelegramUser", back_populates="activities")
    menu_item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="activities")

    def __repr__(self) -> str:
        return f"<UserActivity(id={self.id}, telegram_user_id={self.telegram_user_id}, activity_type={self.activity_type}, menu_id={self.menu_item_id})>"

    def __str__(self) -> str:
        return f"Activity: {self.activity_type} by telegram user {self.telegram_user_id}"