"""Обработка исключений и ошибок."""

from typing import Any, Dict, Optional


class IHearYouException(Exception):
    """Базовое исключение приложения."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Инициализация базового исключения."""
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(IHearYouException):
    """Ошибка валидации данных."""

    pass


class AuthenticationError(IHearYouException):
    """Ошибка аутентификации."""

    pass


class AuthorizationError(IHearYouException):
    """Ошибка авторизации."""

    pass


class NotFoundError(IHearYouException):
    """Ошибка - ресурс не найден."""

    pass


class ConflictError(IHearYouException):
    """Ошибка конфликта данных."""

    pass


class MediaValidationError(IHearYouException):
    """Ошибка валидации медиафайлов."""

    pass
