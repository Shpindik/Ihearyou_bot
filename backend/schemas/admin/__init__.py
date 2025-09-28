"""Административные схемы API."""

from .auth import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminRefreshRequest,
    AdminRefreshResponse,
)
from .analytics import (
    AdminAnalyticsResponse,
)
from .menu import (
    AdminMenuItemResponse,
    AdminMenuItemCreate,
    AdminMenuItemUpdate,
    AdminMenuItemListResponse,
    AdminContentFileResponse,
    AdminContentFileCreate,
    AdminContentFileUpdate,
)
from .notification import (
    AdminNotificationRequest,
    AdminNotificationResponse,
    AdminNotificationListResponse,
    AdminNotificationUpdate,
)
from .question import (
    AdminQuestionResponse,
    AdminQuestionListResponse,
    AdminQuestionAnswer,
)
from .reminder_template import (
    AdminReminderTemplateResponse,
    AdminReminderTemplateListResponse,
    AdminReminderTemplateCreate,
    AdminReminderTemplateUpdate,
)
from .user import (
    AdminTelegramUserResponse,
    AdminTelegramUserListResponse,
)

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
