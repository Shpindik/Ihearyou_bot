"""Модель файлов контента."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.db import Base

from .enums import ContentType


if TYPE_CHECKING:
    from .menu_item import MenuItem


class ContentFile(Base):
    """Модель контента, привязанного к пункту меню (кнопке)."""

    __tablename__ = "content_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    menu_item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("menu_items.id"), nullable=False, unique=True, index=True
    )

    # Тип контента
    content_type: Mapped[ContentType] = mapped_column(String(50), nullable=False, index=True)

    telegram_file_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True, comment="File ID от Telegram для переиспользования медиафайлов"
    )
    caption: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Подпись к медиафайлу (для фото, видео и т.д.)"
    )
    text_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Текстовый контент для типа TEXT")
    external_url: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, index=True, comment="URL для внешних ресурсов (YouTube, VK, Web App, etc)"
    )
    web_app_short_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True, comment="Короткое имя Web App (для type=WEB_APP)"
    )
    local_file_path: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Путь к локальному файлу ДО загрузки в Telegram"
    )

    # Метаданные файла
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Дополнительные поля для медиа
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Ширина изображения/видео")
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Высота изображения/видео")
    duration: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Длительность видео/аудио в секундах"
    )
    thumbnail_telegram_file_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="File ID превью от Telegram"
    )

    # Аудит
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    menu_item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="content", uselist=False)

    def __repr__(self) -> str:
        """Строковое представление для отладки."""
        return f"<ContentFile(id={self.id}, menu_item_id={self.menu_item_id}, content_type={self.content_type})>"

    def __str__(self) -> str:
        """Человекочитаемое строковое представление."""
        return f"Content file: {self.content_type} for menu item {self.menu_item_id}"
