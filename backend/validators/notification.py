"""Валидатор для уведомлений и напоминаний."""

from backend.core.exceptions import NotFoundError, ValidationError


class NotificationValidator:
    """Валидатор для проверки данных уведомлений."""

    def __init__(self):
        """Инициализация валидатора."""

    def validate_user_exists(self, user) -> None:
        """Проверка существования пользователя.

        Args:
            user: Объект пользователя или None

        Raises:
            NotFoundError: Если пользователь не найден
        """
        if not user:
            raise NotFoundError("Пользователь не найден")

    def validate_user_exists_for_id(self, user, user_id: int) -> None:
        """Проверка существования пользователя по ID.

        Args:
            user: Объект пользователя или None
            user_id: ID пользователя

        Raises:
            NotFoundError: Если пользователь не найден
        """
        if not user:
            raise NotFoundError(f"Пользователь с ID {user_id} не найден")

    def validate_notification_exists(self, notification) -> None:
        """Проверка существования уведомления.

        Args:
            notification: Объект уведомления или None

        Raises:
            NotFoundError: Если уведомление не найдено
        """
        if not notification:
            raise NotFoundError("Уведомление не найдено")

    def validate_notification_exists_for_id(self, notification, notification_id: int) -> None:
        """Проверка существования уведомления по ID.

        Args:
            notification: Объект уведомления или None
            notification_id: ID уведомления

        Raises:
            NotFoundError: Если уведомление не найдено
        """
        if not notification:
            raise NotFoundError(f"Уведомление с ID: {notification_id} не найдено")

    def validate_inactive_days(self, inactive_days: int) -> None:
        """Валидация количества дней неактивности.

        Args:
            inactive_days: Количество дней неактивности

        Raises:
            ValidationError: Если значение некорректно
        """
        if not isinstance(inactive_days, int):
            raise ValidationError("Количество дней неактивности должно быть целым числом")

        if inactive_days < 1:
            raise ValidationError("Количество дней неактивности должно быть больше 0")

        if inactive_days > 365:
            raise ValidationError("Количество дней неактивности не должно превышать 365")

    def validate_reminder_interval(self, days_since_last_reminder: int) -> None:
        """Валидация интервала между напоминаниями.

        Args:
            days_since_last_reminder: Минимальный интервал днями

        Raises:
            ValidationError: Если значение некорректно
        """
        if not isinstance(days_since_last_reminder, int):
            raise ValidationError("Интервал между напоминаниями должен быть целым числом")

        if days_since_last_reminder < 1:
            raise ValidationError("Интервал между напоминаниями должен быть больше 0")

        if days_since_last_reminder > 30:
            raise ValidationError("Интервал между напоминаниями не должен превышать 30 дней")

    def validate_message_content(self, message: str) -> None:
        """Валидация содержимого сообщения.

        Args:
            message: Текст сообщения

        Raises:
            ValidationError: Если сообщение некорректно
        """
        if not message or not message.strip():
            raise ValidationError("Сообщение не может быть пустым")

        trimmed = message.strip()
        if len(trimmed) < 10:
            raise ValidationError("Сообщение должно содержать минимум 10 символов")

        if len(message) > 4000:
            raise ValidationError("Сообщение не может превышать 4000 символов")

    def validate_template_variables(self, template: str) -> None:
        """Валидация переменных в шаблоне.

        Args:
            template: Шаблон сообщения

        Raises:
            ValidationError: Если шаблон содержит некорректные переменные
        """
        # Проверяем на наличие потенциально опасных плейсхолдеров
        dangerous_placeholders = ["{system}", "{admin}", "{debug}", "{config}"]

        for placeholder in dangerous_placeholders:
            if placeholder in template:
                raise ValidationError(f"Шаблон содержит запрещенную переменную: {placeholder}")

        # Проверяем баланс фигурных скобок
        open_braces = template.count("{")
        close_braces = template.count("}")

        if open_braces != close_braces:
            raise ValidationError("Несбалансированные фигурные скобки в шаблоне")

    def validate_user_id(self, user_id: int) -> None:
        """Валидация ID пользователя.

        Args:
            user_id: ID пользователя

        Raises:
            ValidationError: Если ID некорректен
        """
        if not isinstance(user_id, int):
            raise ValidationError("ID пользователя должен быть целым числом")

        if user_id <= 0:
            raise ValidationError("ID пользователя должен быть положительным числом")


notification_validator = NotificationValidator()
