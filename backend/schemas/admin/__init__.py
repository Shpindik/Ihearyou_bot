"""Административные схемы API."""

from .analytics import AdminAnalyticsResponse
from .auth import AdminLoginRequest, AdminLoginResponse, AdminRefreshRequest, AdminRefreshResponse
from .menu import (
    AdminContentFileCreate,
    AdminContentFileResponse,
    AdminContentFileUpdate,
    AdminMenuItemCreate,
    AdminMenuItemListResponse,
    AdminMenuItemResponse,
    AdminMenuItemUpdate,
)
from .notification import (
    AdminNotificationListResponse,
    AdminNotificationRequest,
    AdminNotificationResponse,
    AdminNotificationUpdate,
)
from .question import AdminQuestionAnswer, AdminQuestionListResponse, AdminQuestionResponse
from .reminder_template import (
    AdminReminderTemplateCreate,
    AdminReminderTemplateListResponse,
    AdminReminderTemplateResponse,
    AdminReminderTemplateUpdate,
)
from .telegram_user import AdminTelegramUserListResponse, AdminTelegramUserResponse


__all__ = [
    # Auth
    "AdminLoginRequest",
    "AdminLoginResponse",
    "AdminRefreshRequest",
    "AdminRefreshResponse",
    # Analytics
    "AdminAnalyticsResponse",
    # Menu
    "AdminMenuItemResponse",
    "AdminMenuItemCreate",
    "AdminMenuItemUpdate",
    "AdminMenuItemListResponse",
    "AdminContentFileResponse",
    "AdminContentFileCreate",
    "AdminContentFileUpdate",
    # Notifications
    "AdminNotificationRequest",
    "AdminNotificationResponse",
    "AdminNotificationListResponse",
    "AdminNotificationUpdate",
    # Questions
    "AdminQuestionResponse",
    "AdminQuestionListResponse",
    "AdminQuestionAnswer",
    # Reminder Templates
    "AdminReminderTemplateResponse",
    "AdminReminderTemplateListResponse",
    "AdminReminderTemplateCreate",
    "AdminReminderTemplateUpdate",
    # Users
    "AdminTelegramUserResponse",
    "AdminTelegramUserListResponse",
]
