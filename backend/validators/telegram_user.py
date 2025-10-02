"""Валидатор для работы с пользователями Telegram."""

from __future__ import annotations

from backend.core.exceptions import NotFoundError, ValidationError


class TelegramUserValidator:
    """Валидатор бизнес-логики для пользователей Telegram."""

    def __init__(self):
        """Инициализация валидатора Telegram User."""

    def validate_telegram_id_exists(self, telegram_id) -> None:
        """Проверка существования telegram_id.

        Args:
            telegram_id: Telegram ID пользователя или None

        Raises:
            NotFoundError: Если пользователь не найден
        """
        if telegram_id is None:
            raise NotFoundError("Пользователь не найден")

    def validate_telegram_id(self, telegram_id) -> None:
        """Валидация telegram_id.

        Args:
            telegram_id: ID пользователя в Telegram

        Raises:
            ValidationError: Если ID некорректен
        """
        if telegram_id is None:
            raise ValidationError("Отсутствуют данные пользователя в запросе")

        if not isinstance(telegram_id, int):
            raise ValidationError("telegram_id должен быть числом")

        if telegram_id <= 0:
            raise ValidationError("telegram_id должен быть положительным числом")

        if telegram_id < 1000:
            raise ValidationError("telegram_id имеет некорректный формат")

    def validate_user_exists(self, user) -> None:
        """Проверка существования пользователя.

        Args:
            user: Объект пользователя из БД

        Raises:
            ValidationError: Если пользователь не найден
        """
        if not user:
            raise ValidationError("Пользователь не найден")

    def validate_user_id(self, user_id: int) -> None:
        """Валидация ID пользователя для админских операций.

        Args:
            user_id: ID пользователя

        Raises:
            ValidationError: Если ID некорректен
        """
        if user_id <= 0:
            raise ValidationError("ID пользователя должен быть положительным числом")


telegram_user_validator = TelegramUserValidator()
