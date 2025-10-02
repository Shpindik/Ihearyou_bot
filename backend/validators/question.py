"""Валидатор для работы с вопросами пользователей."""

from __future__ import annotations

from backend.core.exceptions import ValidationError


class UserQuestionValidator:
    """Валидатор для работы с вопросами пользователей."""

    def __init__(self):
        """Инициализация валидатора User Question."""

    def validate_user_exists(self, user) -> None:
        """Проверка существования пользователя.

        Args:
            user: Объект пользователя из БД

        Raises:
            ValidationError: Если пользователь не найден

        """
        if not user:
            raise ValidationError("Пользователь не найден. Пользователь должен быть зарегистрирован через Bot API.")

    def _validate_text_content(self, text: str, field_name: str) -> None:
        """Общая валидация текстового содержимого.

        Args:
            text: Текст для валидации
            field_name: Название поля для сообщений об ошибках

        Raises:
            ValidationError: Если текст некорректен

        """
        if not text or not text.strip():
            raise ValidationError(f"{field_name} не может быть пустым")

        trimmed = text.strip()
        if len(trimmed) < 10:
            raise ValidationError(f"{field_name} должен содержать минимум 10 символов")

        if len(text) > 2000:
            raise ValidationError(f"{field_name} не может превышать 2000 символов")

        forbidden_chars = ["<", ">", "&", '"', "'", "\\", ";"]
        if any(char in text for char in forbidden_chars):
            raise ValidationError(f"{field_name} содержит недопустимые символы")

    def validate_question_text(self, question_text: str) -> None:
        """Проверка корректности текста вопроса.

        Args:
            question_text: Текст вопроса

        Raises:
            ValidationError: Если текст вопроса некорректен

        """
        self._validate_text_content(question_text, "Текст вопроса")

    def validate_question_exists(self, question) -> None:
        """Проверка существования вопроса.

        Args:
            question: Объект вопроса из БД

        Raises:
            ValidationError: Если вопрос не найден

        """
        if not question:
            raise ValidationError("Вопрос не найден")

        if question.status.value != "pending":
            raise ValidationError("На данный вопрос уже был дан ответ")

    def validate_answer_text(self, answer_text: str) -> None:
        """Проверка корректности текста ответа.

        Args:
            answer_text: Текст ответа

        Raises:
            ValidationError: Если текст ответа некорректен

        """
        self._validate_text_content(answer_text, "Текст ответа")


user_question_validator = UserQuestionValidator()
