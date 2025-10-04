"""Утилиты для обработки различных типов контента."""

import logging
from typing import Any, Dict, Optional

from aiogram import types
from aiogram.exceptions import TelegramBadRequest

from ..config import settings


logger = logging.getLogger(__name__)


class ContentHandler:
    """Класс для обработки различных типов контента."""

    @staticmethod
    async def send_content(
        message_or_callback: types.Message | types.CallbackQuery, content_data: Dict[str, Any]
    ) -> bool:
        """Отправляет контент пользователю в зависимости от типа.

        Args:
            message_or_callback: Объект сообщения или callback query
            content_data: Данные контента из API

        Returns:
            True если отправка прошла успешно, False иначе
        """
        content_type = content_data.get("content_type")

        if not content_type:
            logger.warning("Content type not specified")
            return False

        try:
            # Определяем куда отправлять - в чат или как ответ на callback
            if isinstance(message_or_callback, types.CallbackQuery):
                bot = message_or_callback.bot
                chat_id = message_or_callback.message.chat.id
                message_id = message_or_callback.message.message_id
            else:
                bot = message_or_callback.bot
                chat_id = message_or_callback.chat.id
                message_id = None

            # Отправляем в зависимости от типа контента
            if content_type == "text":
                await ContentHandler._send_text_content(bot, chat_id, content_data, message_id)
            elif content_type == "photo":
                await ContentHandler._send_photo_content(bot, chat_id, content_data, message_id)
            elif content_type == "video":
                await ContentHandler._send_video_content(bot, chat_id, content_data, message_id)
            elif content_type == "document":
                await ContentHandler._send_document_content(bot, chat_id, content_data, message_id)
            elif content_type in ["youtube_url", "vk_url", "external_url"]:
                await ContentHandler._send_url_content(bot, chat_id, content_data, message_id)
            elif content_type == "web_app":
                await ContentHandler._send_webapp_content(bot, chat_id, content_data, message_id)
            else:
                logger.warning(f"Unknown content type: {content_type}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error sending content: {e}")

            # Отправляем сообщение об ошибке пользователю
            try:
                error_message = (
                    "😔 Произошла ошибка при отправке материала. "
                    "Попробуйте обратиться позже или свяжитесь с администратором."
                )

                if isinstance(message_or_callback, types.CallbackQuery):
                    await message_or_callback.message.edit_text(error_message, parse_mode=settings.parse_mode)
                else:
                    await bot.send_message(chat_id=chat_id, text=error_message)

            except Exception as send_error:
                logger.error(f"Failed to send error message: {send_error}")

            return False

    @staticmethod
    async def _send_text_content(bot, chat_id: int, content_data: Dict[str, Any], message_id: Optional[int]) -> None:
        """Отправляет текстовый контент."""
        text_content = content_data.get("text_content", "")

        if not text_content:
            text_content = "Текстовый контент пуст."

        # Экранируем HTML
        text_content = ContentHandler._escape_html(text_content)

        if message_id:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text_content,
                parse_mode=settings.parse_mode,
                disable_web_page_preview=settings.disable_web_page_preview,
            )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=text_content,
                parse_mode=settings.parse_mode,
                disable_web_page_preview=settings.disable_web_page_preview,
            )

    @staticmethod
    async def _send_photo_content(bot, chat_id: int, content_data: Dict[str, Any], message_id: Optional[int]) -> None:
        """Отправляет фото контент."""
        telegram_file_id = content_data.get("telegram_file_id")
        caption = content_data.get("caption", "")

        if not telegram_file_id:
            logger.warning("Telegram file ID not specified for photo")
            return

        caption = ContentHandler._escape_html(caption)

        if message_id:
            # Обновляем сообщение с фото
            try:
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=types.InputMediaPhoto(
                        media=telegram_file_id, caption=caption, parse_mode=settings.parse_mode
                    ),
                )
            except TelegramBadRequest:
                # Если не удалось обновить (например, фото заменилось на текст),
                # отправляем новое сообщение
                await bot.send_photo(
                    chat_id=chat_id, photo=telegram_file_id, caption=caption, parse_mode=settings.parse_mode
                )
        else:
            await bot.send_photo(
                chat_id=chat_id, photo=telegram_file_id, caption=caption, parse_mode=settings.parse_mode
            )

    @staticmethod
    async def _send_video_content(bot, chat_id: int, content_data: Dict[str, Any], message_id: Optional[int]) -> None:
        """Отправляет видео контент."""
        telegram_file_id = content_data.get("telegram_file_id")
        caption = content_data.get("caption", "")

        if not telegram_file_id:
            logger.warning("Telegram file ID not specified for video")
            return

        caption = ContentHandler._escape_html(caption)

        if message_id:
            try:
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=types.InputMediaVideo(
                        media=telegram_file_id, caption=caption, parse_mode=settings.parse_mode
                    ),
                )
            except TelegramBadRequest:
                await bot.send_video(
                    chat_id=chat_id, video=telegram_file_id, caption=caption, parse_mode=settings.parse_mode
                )
        else:
            await bot.send_video(
                chat_id=chat_id, video=telegram_file_id, caption=caption, parse_mode=settings.parse_mode
            )

    @staticmethod
    async def _send_document_content(
        bot, chat_id: int, content_data: Dict[str, Any], message_id: Optional[int]
    ) -> None:
        """Отправляет документ."""
        telegram_file_id = content_data.get("telegram_file_id")
        caption = content_data.get("caption", "")

        if not telegram_file_id:
            logger.warning("Telegram file ID not specified for document")
            return

        caption = ContentHandler._escape_html(caption)

        if message_id:
            try:
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=types.InputMediaDocument(
                        media=telegram_file_id, caption=caption, parse_mode=settings.parse_mode
                    ),
                )
            except TelegramBadRequest:
                await bot.send_document(
                    chat_id=chat_id, document=telegram_file_id, caption=caption, parse_mode=settings.parse_mode
                )
        else:
            await bot.send_document(
                chat_id=chat_id, document=telegram_file_id, caption=caption, parse_mode=settings.parse_mode
            )

    @staticmethod
    async def _send_url_content(bot, chat_id: int, content_data: Dict[str, Any], message_id: Optional[int]) -> None:
        """Отправляет ссылочный контент."""
        external_url = content_data.get("external_url")
        caption = content_data.get("caption", "")

        if not external_url:
            logger.warning("External URL not specified")
            return

        # Формируем правильную ссылку в зависимости от типа
        content_type = content_data.get("content_type")

        if content_type == "youtube_url":
            emoji = "🎥"
            text = f"{emoji} YouTube видео:\n{external_url}"
        elif content_type == "vk_url":
            emoji = "📹"
            text = f"{emoji} VK видео:\n{external_url}"
        else:
            emoji = "🔗"
            text = f"{emoji} Внешняя ссылка:\n{external_url}"

        if caption:
            caption_html = ContentHandler._escape_html(caption)
            text = f"{caption_html}\n\n{text}"

        if message_id:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                parse_mode=settings.parse_mode,
                disable_web_page_preview=False,  # Показываем превью для ссылок
            )
        else:
            await bot.send_message(
                chat_id=chat_id, text=text, parse_mode=settings.parse_mode, disable_web_page_preview=False
            )

    @staticmethod
    async def _send_webapp_content(bot, chat_id: int, content_data: Dict[str, Any], message_id: Optional[int]) -> None:
        """Отправляет Web App контент."""
        web_app_short_name = content_data.get("web_app_short_name")
        external_url = content_data.get("external_url")
        caption = content_data.get("caption", "")

        # Используем external_url если он есть, иначе web_app_short_name
        web_app_url = external_url or web_app_short_name

        if not web_app_url:
            logger.warning("Web App URL not specified")
            return

        # Если не HTTPS URL, отправляем как обычную ссылку
        if not web_app_url.startswith("http://") and not web_app_url.startswith("https://"):
            logger.warning(f"Non-HTTP URL for Web App: {web_app_url}, sending as text link")
            text = f"🔗 Приложение: {web_app_url}"

            if caption:
                caption_html = ContentHandler._escape_html(caption)
                text = f"{caption_html}\n\n{text}"

            # Отправляем просто текстом без кнопки
            keyboard = None
        else:
            text = f"🌐 Интерактивное приложение: {web_app_short_name or 'Web App'}"

            if caption:
                caption_html = ContentHandler._escape_html(caption)
                text = f"{caption_html}\n\n{text}"

            # Создаем кнопку Web App с HTTPS URL
            keyboard = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="🚀 Открыть приложение", web_app=types.WebAppInfo(url=web_app_url)
                        )
                    ]
                ]
            )

        send_kwargs = {
            "text": text,
            "parse_mode": settings.parse_mode,
            "disable_web_page_preview": settings.disable_web_page_preview,
        }

        if keyboard:
            send_kwargs["reply_markup"] = keyboard

        if message_id:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, **send_kwargs)
        else:
            await bot.send_message(chat_id=chat_id, **send_kwargs)

    @staticmethod
    def _escape_html(text: str) -> str:
        """Экранирует HTML символы для Telegram."""
        if not text:
            return ""

        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
