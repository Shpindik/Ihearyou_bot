"""Валидатор для работы с файлами контента."""

from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status

from backend.core.exceptions import ValidationError
from backend.models.content_file import ContentFile
from backend.models.enums import ContentType
from backend.models.menu_item import MenuItem


class ContentFileValidator:
    """Валидатор для работы с файлами контента."""

    def __init__(self):
        """Инициализация валидатора Content File."""

    def validate_content_file_exists(self, content_file: Optional[ContentFile]) -> ContentFile:
        """Проверка существования файла контента.

        Args:
            content_file: Объект файла контента или None

        Returns:
            ContentFile: Найденный файл контента

        Raises:
            HTTPException: 404 если файл не найден
        """
        if not content_file:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл контента не найден")
        return content_file

    def validate_menu_item_exists(self, menu_item: Optional[MenuItem]) -> MenuItem:
        """Проверка существования пункта меню.

        Args:
            menu_item: Объект пункта меню или None

        Returns:
            MenuItem: Найденный пункт меню

        Raises:
            HTTPException: 404 если пункт меню не найден
        """
        if not menu_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пункт меню не найден")
        return menu_item

    def validate_telegram_file_id_format(self, file_id: Optional[str]) -> None:
        """Проверка формата Telegram file_id."""
        if file_id and len(file_id) < 10:
            raise ValidationError("Некорректный формат telegram_file_id")

    def validate_caption_length(self, caption: Optional[str]) -> None:
        """Проверка длины подписи (макс 1024 символа в Telegram)."""
        if caption and len(caption) > 1024:
            raise ValidationError("Подпись не может превышать 1024 символа")

    def validate_content_type_requirements(
        self,
        content_type: ContentType,
        telegram_file_id: Optional[str] = None,
        text_content: Optional[str] = None,
        external_url: Optional[str] = None,
        local_file_path: Optional[str] = None,
        web_app_short_name: Optional[str] = None,
    ) -> None:
        """Обновленная проверка требований для типа контента.

        Args:
            content_type: Тип контента
            telegram_file_id: File ID от Telegram
            text_content: Текстовый контент
            external_url: Внешний URL
            local_file_path: Путь к локальному файлу
            web_app_short_name: Короткое имя Web App

        Raises:
            ValidationError: Если данные не соответствуют типу контента
        """
        if content_type == ContentType.TEXT:
            if not text_content:
                raise ValidationError("Для TEXT необходим text_content")

        elif content_type in [
            ContentType.PHOTO,
            ContentType.VIDEO,
            ContentType.AUDIO,
            ContentType.VOICE,
            ContentType.VIDEO_NOTE,
            ContentType.ANIMATION,
            ContentType.STICKER,
            ContentType.DOCUMENT,
        ]:
            # Должен быть либо telegram_file_id, либо local_file_path для загрузки
            if not telegram_file_id and not local_file_path:
                raise ValidationError(f"Для {content_type.value} необходим telegram_file_id или local_file_path")

        elif content_type in [ContentType.YOUTUBE_URL, ContentType.VK_URL, ContentType.EXTERNAL_URL]:
            if not external_url:
                raise ValidationError(f"Для {content_type.value} необходим external_url")

        elif content_type == ContentType.WEB_APP:
            if not external_url and not web_app_short_name:
                raise ValidationError("Для WEB_APP необходим external_url или web_app_short_name")

    def validate_one_content_per_menu_item(self, menu_item_id: int, existing_content: Optional[ContentFile]) -> None:
        """Проверка, что у MenuItem еще нет контента."""
        if existing_content:
            raise ValidationError(
                f"У пункта меню {menu_item_id} уже есть контент. " "Один MenuItem может иметь только один ContentFile."
            )

    def validate_file_size(self, file_size: Optional[int], max_size: int = 50 * 1024 * 1024) -> None:
        """Проверка размера файла.

        Args:
            file_size: Размер файла в байтах
            max_size: Максимальный размер файла в байтах (по умолчанию 50MB)

        Raises:
            ValidationError: Если файл слишком большой
        """
        if file_size is not None and file_size > max_size:
            raise ValidationError(f"Размер файла превышает максимально допустимый ({max_size // (1024*1024)}MB)")

    def validate_url_format(self, url: Optional[str]) -> None:
        """Проверка формата URL.

        Args:
            url: URL для проверки

        Raises:
            ValidationError: Если URL имеет неверный формат
        """
        if url and not (url.startswith("http://") or url.startswith("https://")):
            raise ValidationError("URL должен начинаться с http:// или https://")


content_file_validator = ContentFileValidator()
