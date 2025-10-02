"""Инициализация CRUD пакета."""

from .analytics import AnalyticsCRUD, analytics_crud
from .base import BaseCRUD
from .content_file import ContentFileCRUD, content_file_crud
from .menu_item import MenuItemCRUD, menu_item_crud
from .notification import NotificationCRUD, notification_crud
from .question import QuestionCRUD, question_crud
from .reminder_template import ReminderTemplateCRUD, reminder_template_crud
from .telegram_user import TelegramUserCRUD, telegram_user_crud
from .user_activity import UserActivityCRUD, user_activity_crud


__all__ = [
    "AnalyticsCRUD",
    "BaseCRUD",
    "MenuItemCRUD",
    "ContentFileCRUD",
    "NotificationCRUD",
    "QuestionCRUD",
    "ReminderTemplateCRUD",
    "TelegramUserCRUD",
    "UserActivityCRUD",
    "analytics_crud",
    "menu_item_crud",
    "content_file_crud",
    "notification_crud",
    "question_crud",
    "reminder_template_crud",
    "telegram_user_crud",
    "user_activity_crud",
]
