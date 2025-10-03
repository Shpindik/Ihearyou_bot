"""Модель шаблонов сообщений для различных типов коммуникаций."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.db import Base


if TYPE_CHECKING:
    from .notification import Notification


class MessageTemplate(Base):
    """Модель шаблонов сообщений для различных типов коммуникаций."""

    __tablename__ = "message_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    message_template: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Связи
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="template", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Строковое представление для отладки."""
        return f"<MessageTemplate(id={self.id}, name='{self.name}')>"

    def __str__(self) -> str:
        """Человекочитаемое строковое представление."""
        return f"Template: {self.name}"
