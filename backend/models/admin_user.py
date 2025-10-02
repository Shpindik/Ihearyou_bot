"""Модель администраторов системы."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.db import Base

from .enums import AdminRole


if TYPE_CHECKING:
    from .question import UserQuestion


class AdminUser(Base):
    """Модель администраторов системы."""

    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, unique=True, comment="Email администратора (логин + уведомления)"
    )
    role: Mapped[AdminRole] = mapped_column(String(20), default=AdminRole.ADMIN, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Связи
    answered_questions: Mapped[List["UserQuestion"]] = relationship("UserQuestion", back_populates="admin_user")

    def __repr__(self) -> str:
        """Строковое представление для отладки."""
        return f"<AdminUser(id={self.id}, username={self.username}, email={self.email}, role={self.role})>"

    def __str__(self) -> str:
        """Человекочитаемое строковое представление."""
        return f"Admin {self.username} ({self.email}) [{self.role}]"
