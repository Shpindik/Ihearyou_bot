"""Enum типы для моделей."""

import enum


class ItemType(str, enum.Enum):
    """Тип пункта меню в ТГ-боте."""

    NAVIGATION = "navigation"  # Навигационная кнопка (имеет children)
    CONTENT = "content"  # Контентная кнопка (имеет content)


class ContentType(str, enum.Enum):
    """Типы контента для Telegram Bot."""

    # Текстовый контент
    TEXT = "text"

    # Медиафайлы Telegram
    PHOTO = "photo"  # Фото (до 10MB)
    VIDEO = "video"  # Видео (до 50MB)
    DOCUMENT = "document"  # Документ (включая PDF)

    # Внешние ссылки
    YOUTUBE_URL = "youtube_url"  # Ссылка на YouTube
    VK_URL = "vk_url"  # Ссылка на VK Video
    EXTERNAL_URL = "external_url"  # Любая HTTP/HTTPS ссылка
    WEB_APP = "web_app"  # Telegram Web App (miniapp)

    # Медиафайлы (если понадобятся)
    AUDIO = "audio"  # Аудио (музыка, подкасты)
    ANIMATION = "animation"  # GIF/анимация

    # Специальные (если понадобятся)
    LOCATION = "location"  # Геолокация


class TokenType(str, enum.Enum):
    """Типы JWT токенов"""

    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"


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
    CONTENT_VIEW = "content_view"  # Общий просмотр контента

    # Оценка и обратная связь
    RATING = "rating"  # Оценка полезности материала (1-5)
    QUESTION_ASK = "question_ask"  # Задавание вопросов
    QUESTION_CLICK = "question_click"  # Клик "Задать вопрос"
    LETTER_SEND = "letter_send"  # Отправка письма
    LETTER_CLICK = "letter_click"  # Клик "Написать письмо"

    # Аналитика и статистика
    SECTION_ENTER = "section_enter"  # Вход в раздел
    MATERIAL_OPEN = "material_open"  # Открытие конкретного материала


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
