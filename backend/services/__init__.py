"""Инициализация сервисов."""

from .admin_user import AdminUserService, admin_user_service
from .content_file import ContentFileService, content_file_service
from .menu_item import MenuItemService, menu_item_service
from .message_template import MessageTemplateService, message_template_service
from .notification import NotificationService, notification_service
from .question import UserQuestionService, user_question_service
from .telegram_user import TelegramUserService, telegram_user_service
from .user_activity import UserActivityService, user_activity_service


__all__ = [
    # Services
    "AdminUserService",
    "ContentFileService",
    "MenuItemService",
    "NotificationService",
    "UserQuestionService",
    "MessageTemplateService",
    "TelegramUserService",
    "UserActivityService",
    # Service instances
    "admin_user_service",
    "content_file_service",
    "menu_item_service",
    "notification_service",
    "user_question_service",
    "message_template_service",
    "telegram_user_service",
    "user_activity_service",
]
