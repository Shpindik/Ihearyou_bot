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
    """Типы активности пользователей"""

    # Основная навигация и взаимодействие
    START_COMMAND = "start_command"  # Команда /start - начало взаимодействия
    NAVIGATION = "navigation"  # Навигация по меню
    SEARCH = "search"  # Поиск по ключевым словам

    # Работа с контентом
    TEXT_VIEW = "text_view"  # Просмотр текстовых материалов
    IMAGE_VIEW = "image_view"  # Просмотр изображений
    VIDEO_VIEW = "video_view"  # Просмотр видео (YouTube, VK)
    PDF_DOWNLOAD = "pdf_download"  # Скачивание PDF документов
    MEDIA_VIEW = "media_view"  # Общий просмотр медиа

    # Оценка и обратная связь
    RATING = "rating"  # Оценка полезности материала (1-5)
    QUESTION_ASK = "question_ask"  # Задавание вопросов
    QUESTION_CLICK = "question_click"  # Клик "Задать вопрос"
    LETTER_SEND = "letter_send"  # Отправка письма
    LETTER_CLICK = "letter_click"  # Клик "Написать письмо"

    # Аналитика и статистика
    SECTION_ENTER = "section_enter"  # Вход в раздел
    MATERIAL_OPEN = "material_open"  # Открытие конкретного материала

    # WebApp взаимодействие (только факт открытия)
    # WEBAPP_OPENED = "webapp_opened"         # Открытие WebApp кнопки
    # (можно реализовать, если надо для статистики, просто чуть сложнее реализовать)


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
