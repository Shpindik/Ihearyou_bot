"""Административные схемы API."""

from .admin_user import (
    AdminUserCreate,
    AdminUserListResponse,
    AdminUserPasswordUpdate,
    AdminUserResponse,
    AdminUserUpdate,
)
from .analytics import AdminAnalyticsRequest, AdminAnalyticsResponse
from .auth import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminMeResponse,
    AdminPasswordResetConfirmRequest,
    AdminPasswordResetRequest,
    AdminPasswordResetSuccessResponse,
    AdminRefreshRequest,
    AdminRefreshResponse,
)
from .menu import (
    AdminContentFileCreate,
    AdminContentFileResponse,
    AdminContentFileUpdate,
    AdminMenuItemCreate,
    AdminMenuItemListResponse,
    AdminMenuItemResponse,
    AdminMenuItemUpdate,
)
from .message_template import (
    AdminMessageTemplateCreate,
    AdminMessageTemplateListResponse,
    AdminMessageTemplateResponse,
    AdminMessageTemplateUpdate,
)
from .notification import (
    AdminNotificationListResponse,
    AdminNotificationRequest,
    AdminNotificationResponse,
    AdminNotificationUpdate,
)
from .question import AdminQuestionAnswer, AdminQuestionListResponse, AdminQuestionResponse
from .telegram_user import AdminTelegramUserListResponse, AdminTelegramUserResponse


__all__ = [
    # Auth
    "AdminLoginRequest",
    "AdminLoginResponse",
    "AdminRefreshRequest",
    "AdminRefreshResponse",
    "AdminMeResponse",
    "AdminPasswordResetRequest",
    "AdminPasswordResetConfirmRequest",
    "AdminPasswordResetSuccessResponse",
    # Admin Management
    "AdminUserResponse",
    "AdminUserListResponse",
    "AdminUserCreate",
    "AdminUserUpdate",
    "AdminUserPasswordUpdate",
    # Analytics
    "AdminAnalyticsRequest",
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
    # Message Templates
    "AdminMessageTemplateResponse",
    "AdminMessageTemplateListResponse",
    "AdminMessageTemplateCreate",
    "AdminMessageTemplateUpdate",
    # Users
    "AdminTelegramUserResponse",
    "AdminTelegramUserListResponse",
]
