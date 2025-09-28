"""Модель структуры меню бота."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from decimal import Decimal
from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from .enums import AccessLevel

if TYPE_CHECKING:
    from .user_activity import UserActivity
    from .content_file import ContentFile


class MenuItem(Base):
    """Модель пунктов меню с унифицированным контентом."""
    
    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Иерархия меню
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("menu_items.id"), nullable=True, index=True
    )
    
    # Сообщение бота
    bot_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Управление
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    access_level: Mapped[AccessLevel] = mapped_column(String(20), default=AccessLevel.FREE, nullable=False, index=True)
    
    # Статистика
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    download_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rating_sum: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rating_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_rating: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(3, 2), nullable=True)
    
    # Аудит
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Связи
    parent: Mapped[Optional["MenuItem"]] = relationship(
        "MenuItem", remote_side=[id], back_populates="children"
    )
    children: Mapped[List["MenuItem"]] = relationship(
        "MenuItem", back_populates="parent", cascade="all, delete-orphan"
    )
    activities: Mapped[List["UserActivity"]] = relationship(
        "UserActivity", back_populates="menu_item"
    )
    content_files: Mapped[List["ContentFile"]] = relationship(
        "ContentFile", back_populates="menu_item", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<MenuItem(id={self.id}, title='{self.title}', is_active={self.is_active})>"

    def __str__(self) -> str:
        return f"Menu: {self.title}"