"""Enum типы для моделей."""

import enum


class ContentType(str, enum.Enum):
    """Типы контента."""

    IMAGE = "image"
    VIDEO = "video"
    PDF = "pdf"
    DOCUMENT = "document"
    YOUTUBE = "youtube"
    VK = "vk"
    TEXT = "text"


class ActivityType(str, enum.Enum):
    """Типы активности пользователей."""

    NAVIGATION = "navigation"
    SEARCH = "search"
    RATING = "rating"
    QUESTION = "question"
    MEDIA_VIEW = "media_view"


class QuestionStatus(str, enum.Enum):
    """Статусы вопросов пользователей."""

    PENDING = "pending"
    ANSWERED = "answered"
    CLOSED = "closed"


class NotificationStatus(str, enum.Enum):
    """Статусы уведомлений."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class AdminRole(str, enum.Enum):
    """Роли администраторов."""

    ADMIN = "admin"
    MODERATOR = "moderator"


class SubscriptionType(str, enum.Enum):
    """Типы подписки пользователей."""

    FREE = "free"
    PREMIUM = "premium"


class AccessLevel(str, enum.Enum):
    """Уровни доступа к контенту."""

    FREE = "free"
    PREMIUM = "premium"
