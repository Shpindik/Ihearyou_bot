"""Модель вопросов пользователей."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.db import Base

from .enums import QuestionStatus


if TYPE_CHECKING:
    from .admin_user import AdminUser
    from .telegram_user import TelegramUser


class UserQuestion(Base):
    """Модель вопросов пользователей."""

    __tablename__ = "user_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("telegram_users.id"), nullable=False, index=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    answer_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[QuestionStatus] = mapped_column(
        String(20), default=QuestionStatus.PENDING, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
    answered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    admin_user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("admin_users.id"), nullable=True, index=True
    )

    # Связи
    telegram_user: Mapped["TelegramUser"] = relationship("TelegramUser", back_populates="questions")
    admin_user: Mapped[Optional["AdminUser"]] = relationship("AdminUser", back_populates="answered_questions")

    def __repr__(self) -> str:
        """Строковое представление для отладки."""
        return f"<UserQuestion(id={self.id}, telegram_user_id={self.telegram_user_id}, status={self.status})>"

    def __str__(self) -> str:
        """Человекочитаемое строковое представление."""
        return f"Question from telegram user {self.telegram_user_id} ({self.status})"
