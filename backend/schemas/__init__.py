"""Инициализация схем и экспорт."""

# Административные схемы
from .admin import (
    AdminAnalyticsResponse,
    AdminContentFileCreate,
    AdminContentFileResponse,
    AdminContentFileUpdate,
    AdminLoginRequest,
    AdminLoginResponse,
    AdminMenuItemCreate,
    AdminMenuItemListResponse,
    AdminMenuItemResponse,
    AdminMenuItemUpdate,
    AdminNotificationListResponse,
    AdminNotificationRequest,
    AdminNotificationResponse,
    AdminNotificationUpdate,
    AdminQuestionAnswer,
    AdminQuestionListResponse,
    AdminQuestionResponse,
    AdminRefreshRequest,
    AdminRefreshResponse,
    AdminReminderTemplateCreate,
    AdminReminderTemplateListResponse,
    AdminReminderTemplateResponse,
    AdminReminderTemplateUpdate,
    AdminTelegramUserListResponse,
    AdminTelegramUserResponse,
)

# Публичные схемы
from .public import (
    ContentFileResponse,
    MenuContentResponse,
    MenuItemResponse,
    RatingRequest,
    RatingResponse,
    SearchListResponse,
    UserActivityRequest,
    UserActivityResponse,
    UserQuestionCreate,
    UserQuestionResponse,
)

# Webhook схемы
from .webhook import TelegramWebhookRequest, TelegramWebhookResponse


__all__ = [
    # Admin schemas
    "AdminLoginRequest",
    "AdminLoginResponse",
    "AdminRefreshRequest",
    "AdminRefreshResponse",
    "AdminAnalyticsResponse",
    "AdminMenuItemResponse",
    "AdminMenuItemCreate",
    "AdminMenuItemUpdate",
    "AdminMenuItemListResponse",
    "AdminContentFileResponse",
    "AdminContentFileCreate",
    "AdminContentFileUpdate",
    "AdminNotificationRequest",
    "AdminNotificationResponse",
    "AdminNotificationListResponse",
    "AdminNotificationUpdate",
    "AdminQuestionResponse",
    "AdminQuestionListResponse",
    "AdminQuestionAnswer",
    "AdminReminderTemplateResponse",
    "AdminReminderTemplateListResponse",
    "AdminReminderTemplateCreate",
    "AdminReminderTemplateUpdate",
    "AdminTelegramUserResponse",
    "AdminTelegramUserListResponse",
    # Public schemas
    "MenuItemResponse",
    "MenuContentResponse",
    "ContentFileResponse",
    "RatingRequest",
    "RatingResponse",
    "SearchListResponse",
    "UserActivityRequest",
    "UserActivityResponse",
    "UserQuestionCreate",
    "UserQuestionResponse",
    # Webhook schemas
    "TelegramWebhookRequest",
    "TelegramWebhookResponse",
]
