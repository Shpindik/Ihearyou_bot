"""Модель файлов контента."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from .enums import ContentType

if TYPE_CHECKING:
    from .menu import MenuItem


class ContentFile(Base):
    """Модель файлов контента."""
    
    __tablename__ = "content_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    menu_item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("menu_items.id"), nullable=False, index=True
    )
    content_type: Mapped[ContentType] = mapped_column(String(50), nullable=False)
    content_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Связи
    menu_item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="content_files")

    def __repr__(self) -> str:
        return f"<ContentFile(id={self.id}, menu_item_id={self.menu_item_id}, content_type={self.content_type})>"

    def __str__(self) -> str:
        return f"Content file: {self.content_type} for menu item {self.menu_item_id}"
