"""Инициализация валидаторов."""

from .admin_user import AdminUserValidator, admin_user_validator
from .content_file import ContentFileValidator, content_file_validator
from .menu_item import MenuItemValidator, menu_item_validator
from .message_template import MessageTemplateValidator, message_template_validator
from .notification import NotificationValidator, notification_validator
from .question import UserQuestionValidator, user_question_validator
from .telegram_user import TelegramUserValidator, telegram_user_validator
from .user_activity import UserActivityValidator, user_activity_validator


__all__ = [
    # Validators
    "AdminUserValidator",
    "ContentFileValidator",
    "MenuItemValidator",
    "NotificationValidator",
    "UserQuestionValidator",
    "MessageTemplateValidator",
    "TelegramUserValidator",
    "UserActivityValidator",
    # Validator instances
    "admin_user_validator",
    "content_file_validator",
    "menu_item_validator",
    "notification_validator",
    "user_question_validator",
    "message_template_validator",
    "telegram_user_validator",
    "user_activity_validator",
]
