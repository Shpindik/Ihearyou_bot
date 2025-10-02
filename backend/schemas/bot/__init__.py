"""Схемы для Bot API."""

from .reminder import InactiveListUserResponse, InactiveUserResponse
from .reminder_template import BotReminderTemplateResponse
from .telegram_user import TelegramUserRequest, TelegramUserResponse


__all__ = [
    # Reminder
    "InactiveListUserResponse",
    "InactiveUserResponse",
    # Reminder template
    "BotReminderTemplateResponse",
    # Telegram user
    "TelegramUserRequest",
    "TelegramUserResponse",
]
