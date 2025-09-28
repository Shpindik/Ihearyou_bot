"""Инициализация схем и экспорт."""

# Административные схемы
from .admin import *

# Публичные схемы
from .public import *

# Webhook схемы
from .webhook import (
    TelegramWebhookRequest,
    TelegramWebhookResponse,
)

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
