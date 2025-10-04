"""Валидатор для работы с вопросами пользователей."""

from __future__ import annotations

from fastapi import HTTPException, status


class UserQuestionValidator:
    """Валидатор для работы с вопросами пользователей."""

    def __init__(self):
        """Инициализация валидатора User Question."""

    def validate_user_exists(self, user) -> None:
        """Проверка существования пользователя.

        Args:
            user: Объект пользователя из БД

        Raises:
            HTTPException: Если пользователь не найден

        """
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден. Пользователь должен быть зарегистрирован через Bot API.",
            )

    def _validate_text_content(self, text: str, field_name: str) -> None:
        """Общая валидация текстового содержимого.

        Args:
            text: Текст для валидации
            field_name: Название поля для сообщений об ошибках

        Raises:
            HTTPException: Если текст содержит недопустимые символы

        """
        forbidden_chars = ["<", ">", "&", '"', "'", "\\", ";"]
        if any(char in text for char in forbidden_chars):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field_name} содержит недопустимые символы"
            )

    def validate_question_text(self, question_text: str) -> None:
        """Проверка корректности текста вопроса.

        Args:
            question_text: Текст вопроса

        Raises:
            HTTPException: Если текст вопроса некорректен

        """
        self._validate_text_content(question_text, "Текст вопроса")

    def validate_question_exists(self, question) -> None:
        """Проверка существования вопроса.

        Args:
            question: Объект вопроса из БД

        Raises:
            HTTPException: Если вопрос не найден или уже отвечен

        """
        if not question:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден")

        if question.status != "pending":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="На данный вопрос уже был дан ответ")

    def validate_answer_text(self, answer_text: str) -> None:
        """Проверка корректности текста ответа.

        Args:
            answer_text: Текст ответа

        Raises:
            HTTPException: Если текст ответа некорректен

        """
        self._validate_text_content(answer_text, "Текст ответа")


user_question_validator = UserQuestionValidator()
