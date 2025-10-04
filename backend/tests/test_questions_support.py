"""Тесты системы поддержки вопросов."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.question import QuestionCRUD
from backend.models.telegram_user import TelegramUser
from backend.schemas.public.question import UserQuestionCreate
from backend.services.question import UserQuestionService
from backend.validators.question import UserQuestionValidator


@pytest.mark.unit
class TestPublicQuestionAPI:
    """Тесты API эндпоинтов для вопросов пользователей."""

    @pytest.mark.asyncio
    async def test_create_user_question_success(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser]
    ):
        """Тест успешного создания вопроса пользователем."""
        # Arrange
        endpoint = "/api/v1/public/user-questions"
        user = telegram_users_fixture[0]
        question_data = {
            "telegram_user_id": user.telegram_id,
            "question_text": "Это тестовый вопрос для проверки функциональности",
        }
        expected_status_code = 201

        # Act
        response = await async_client.post(endpoint, json=question_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        
        assert "question_text" in data
        assert "status" in data
        assert data["question_text"] == question_data["question_text"]
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_create_user_question_user_not_found(self, async_client: AsyncClient):
        """Тест создания вопроса для несуществующего пользователя."""
        # Arrange
        endpoint = "/api/v1/public/user-questions"
        non_existent_user_id = 999999999
        question_data = {
            "telegram_user_id": non_existent_user_id,
            "question_text": "Тестовый вопрос"
        }
        expected_status_code = 404
        expected_error_message = "Пользователь не найден"

        # Act
        response = await async_client.post(endpoint, json=question_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert expected_error_message in data["detail"]

    @pytest.mark.parametrize(
        "question_text,expected_status",
        [
            ("", 422),  # Пустой текст - Pydantic validation
            ("Коротко", 422),  # Слишком короткий текст - Pydantic validation
        ],
    )
    @pytest.mark.asyncio
    async def test_create_user_question_invalid_text(self, async_client: AsyncClient, question_text, expected_status):
        """Тест создания вопроса с некорректным текстом."""
        # Arrange
        endpoint = "/api/v1/public/user-questions"
        question_data = {
            "telegram_user_id": 123456789,
            "question_text": question_text
        }

        # Act
        response = await async_client.post(endpoint, json=question_data)

        # Assert
        assert response.status_code == expected_status

    @pytest.mark.asyncio
    async def test_create_user_question_too_long(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser]
    ):
        """Тест создания вопроса со слишком длинным текстом."""
        # Arrange
        endpoint = "/api/v1/public/user-questions"
        user = telegram_users_fixture[0]
        long_text = "А" * 2001  # Превышает лимит в 2000 символов
        question_data = {
            "telegram_user_id": user.telegram_id,
            "question_text": long_text
        }
        expected_status_code = 422

        # Act
        response = await async_client.post(endpoint, json=question_data)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.asyncio
    async def test_create_user_question_forbidden_chars(
        self, async_client: AsyncClient, telegram_users_fixture: list[TelegramUser]
    ):
        """Тест создания вопроса с запрещенными символами."""
        # Arrange
        endpoint = "/api/v1/public/user-questions"
        user = telegram_users_fixture[0]
        question_data = {
            "telegram_user_id": user.telegram_id,
            "question_text": "Вопрос с запрещенными символами: <script>alert('hack')</script>",
        }
        expected_status_code = 400
        expected_error_message = "содержит недопустимые символы"

        # Act
        response = await async_client.post(endpoint, json=question_data)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        assert expected_error_message in data["detail"]

    @pytest.mark.asyncio
    async def test_admin_can_list_questions(self, admin_client: AsyncClient):
        """Тест получения списка вопросов админом."""
        # Arrange
        endpoint = "/api/v1/admin/user-questions/"
        expected_status_code = 200

        # Act
        response = await admin_client.get(endpoint)

        # Assert
        assert response.status_code == expected_status_code
        data = response.json()
        
        assert isinstance(data, dict)
        assert isinstance(data.get("items"), list)


@pytest.mark.unit
class TestUserQuestionService:
    """Тесты сервиса UserQuestionService."""

    @pytest.mark.asyncio
    async def test_create_user_question_success(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser]):
        """Тест успешного создания вопроса пользователем."""
        # Arrange
        service = UserQuestionService()
        user = telegram_users_fixture[0]
        question_data = UserQuestionCreate(
            telegram_user_id=user.telegram_id,
            question_text="Это тестовый вопрос для проверки функциональности сервиса"
        )

        # Act
        result = await service.create_user_question(question_data, db)

        # Assert
        assert result.question_text == question_data.question_text
        assert result.status == "pending"
        assert result.answer_text is None

    @pytest.mark.parametrize(
        "telegram_user_id,question_text,expected_error",
        [
            (999999999, "Это тестовый вопрос с достаточной длиной", "Пользователь не найден"),  # Несуществующий пользователь
        ],
    )
    @pytest.mark.asyncio
    async def test_create_user_question_invalid(
        self, db: AsyncSession, telegram_user_id, question_text, expected_error
    ):
        """Тест создания вопроса с некорректными данными."""
        # Arrange
        service = UserQuestionService()
        question_data = UserQuestionCreate(
            telegram_user_id=telegram_user_id,
            question_text=question_text
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.create_user_question(question_data, db)

        assert expected_error in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_admin_questions_success(self, db: AsyncSession):
        """Тест успешного получения списка вопросов для администраторов."""
        # Arrange
        service = UserQuestionService()
        page = 1
        limit = 10

        # Act
        result = await service.get_admin_questions(db, page=page, limit=limit)

        # Assert
        assert hasattr(result, "items")
        assert hasattr(result, "total")
        assert hasattr(result, "page")
        assert hasattr(result, "limit")
        assert hasattr(result, "pages")
        assert result.page == page
        assert result.limit == limit

    @pytest.mark.asyncio
    async def test_get_admin_questions_with_status_filter(self, db: AsyncSession):
        """Тест получения вопросов с фильтром по статусу."""
        # Arrange
        service = UserQuestionService()
        status = "pending"
        page = 1
        limit = 5

        # Act
        result = await service.get_admin_questions(db, status=status, page=page, limit=limit)

        # Assert
        assert result.page == page
        assert result.limit == limit
        # Все вопросы должны иметь статус pending
        for item in result.items:
            assert item.status == status

    @pytest.mark.asyncio
    async def test_get_questions_statistics(self, db: AsyncSession):
        """Тест получения статистики по вопросам."""
        # Arrange
        service = UserQuestionService()

        # Act
        result = await service.get_questions_statistics(db)

        # Assert
        assert isinstance(result, dict)
        required_keys = ["total", "pending", "answered"]
        for key in required_keys:
            assert key in result
        assert result["total"] >= result["pending"] + result["answered"]


@pytest.mark.unit
class TestQuestionCRUD:
    """Тесты CRUD операций для вопросов пользователей."""

    @pytest.mark.asyncio
    async def test_create_question_success(self, db: AsyncSession, telegram_users_fixture: list[TelegramUser]):
        """Тест успешного создания вопроса."""
        # Arrange
        crud = QuestionCRUD()
        user = telegram_users_fixture[0]
        question_text = "Тестовый вопрос для проверки CRUD операций"

        # Act
        result = await crud.create_question(db=db, telegram_user_id=user.id, question_text=question_text)

        # Assert
        assert result.telegram_user_id == user.id
        assert result.question_text == question_text
        assert result.status == "pending"
        assert result.answer_text is None
        assert result.admin_user_id is None
        assert result.answered_at is None

    @pytest.mark.parametrize(
        "status,expected_status",
        [
            (None, None),  # Все вопросы
            ("pending", "pending"),  # Только pending
        ],
    )
    @pytest.mark.asyncio
    async def test_get_questions_by_status(self, db: AsyncSession, status, expected_status):
        """Тест получения вопросов с фильтром по статусу."""
        # Arrange
        crud = QuestionCRUD()
        skip = 0
        limit = 10

        # Act
        result = await crud.get_questions_by_status(db, status=status, skip=skip, limit=limit)

        # Assert
        assert isinstance(result, list)
        assert len(result) >= 0

        if expected_status:
            for question in result:
                assert question.status == expected_status

    @pytest.mark.asyncio
    async def test_count_questions_by_status_all(self, db: AsyncSession):
        """Тест подсчета всех вопросов."""
        # Arrange
        crud = QuestionCRUD()

        # Act
        total_count = await crud.count_questions_by_status(db)
        pending_count = await crud.count_questions_by_status(db, "pending")

        # Assert
        assert isinstance(total_count, int)
        assert isinstance(pending_count, int)
        assert total_count >= pending_count

    @pytest.mark.asyncio
    async def test_get_questions_statistics(self, db: AsyncSession):
        """Тест получения статистики вопросов."""
        # Arrange
        crud = QuestionCRUD()

        # Act
        result = await crud.get_questions_statistics(db)

        # Assert
        assert isinstance(result, dict)
        required_keys = ["total", "pending", "answered"]
        for key in required_keys:
            assert key in result
        assert result["total"] == result["pending"] + result["answered"]

    @pytest.mark.asyncio
    async def test_answer_question_success(
        self, db: AsyncSession, telegram_users_fixture: list[TelegramUser], admin_user
    ):
        """Тест успешного ответа на вопрос."""
        # Arrange
        crud = QuestionCRUD()
        user = telegram_users_fixture[0]
        question_text = "Вопрос для ответа"
        answer_text = "Это ответ на вопрос"

        # Создаем вопрос
        question = await crud.create_question(db=db, telegram_user_id=user.id, question_text=question_text)

        # Act
        result = await crud.answer_question(
            db=db, question_id=question.id, answer_text=answer_text, admin_user_id=admin_user.id
        )

        # Assert
        assert result.id == question.id
        assert result.answer_text == answer_text
        assert result.status == "answered"
        assert result.admin_user_id == admin_user.id
        assert result.answered_at is not None


@pytest.mark.unit
class TestUserQuestionValidator:
    """Тесты валидатора UserQuestionValidator."""

    def test_validate_user_exists_success(self, telegram_users_fixture: list[TelegramUser]):
        """Тест успешной валидации существующего пользователя."""
        # Arrange
        validator = UserQuestionValidator()
        existing_user = telegram_users_fixture[0]

        # Act & Assert
        # Не должно вызывать исключений
        validator.validate_user_exists(existing_user)

    def test_validate_user_exists_none(self):
        """Тест валидации несуществующего пользователя (None)."""
        # Arrange
        validator = UserQuestionValidator()
        expected_error_message = "Пользователь не найден"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validator.validate_user_exists(None)

        assert expected_error_message in str(exc_info.value)

    @pytest.mark.parametrize(
        "valid_question_text",
        [
            "Это вопрос с достаточной длиной для валидации",  # Нормальный текст
            "А" * 10,  # Минимальная длина
            "Вопрос без запрещенных символов и достаточной длины для прохождения валидации",  # Средний текст
            "А" * 2000,  # Максимальная длина
        ],
    )
    def test_validate_question_text_success(self, valid_question_text):
        """Тест успешной валидации корректного текста вопроса."""
        # Arrange
        validator = UserQuestionValidator()

        # Act & Assert - не должно вызывать исключений
        validator.validate_question_text(valid_question_text)

    @pytest.mark.parametrize(
        "invalid_question_text, expected_error",
        [
            ("Вопрос с <script>", "недопустимые символы"),
            ("Вопрос с > символом", "недопустимые символы"),
            ("Вопрос с & амперсандом", "недопустимые символы"),
            ('Вопрос с " кавычками', "недопустимые символы"),
            ("Вопрос с ' апострофом", "недопустимые символы"),
            ("Вопрос с \\ бэкслешем", "недопустимые символы"),
            ("Вопрос с ; точкой с запятой", "недопустимые символы"),
        ],
    )
    def test_validate_question_text_invalid(self, invalid_question_text, expected_error):
        """Тест валидации некорректного текста вопроса."""
        # Arrange
        validator = UserQuestionValidator()

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validator.validate_question_text(invalid_question_text)

        assert expected_error in str(exc_info.value)

    def test_validate_question_exists_success(self):
        """Тест успешной валидации существующего вопроса."""
        # Arrange
        validator = UserQuestionValidator()
        mock_question = type("MockQuestion", (), {"status": "pending"})()

        # Act & Assert
        # Не должно вызывать исключений
        validator.validate_question_exists(mock_question)

    def test_validate_question_exists_none(self):
        """Тест валидации несуществующего вопроса (None)."""
        # Arrange
        validator = UserQuestionValidator()
        expected_error_message = "Вопрос не найден"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validator.validate_question_exists(None)

        assert expected_error_message in str(exc_info.value)

    def test_validate_question_exists_already_answered(self):
        """Тест валидации вопроса, на который уже ответили."""
        # Arrange
        validator = UserQuestionValidator()
        mock_question = type("MockQuestion", (), {"status": "answered"})()
        expected_error_message = "уже был дан ответ"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validator.validate_question_exists(mock_question)

        assert expected_error_message in str(exc_info.value)

    @pytest.mark.parametrize(
        "valid_answer_text",
        [
            "Это ответ с достаточной длиной для валидации",
            "А" * 10,  # Минимальная длина
            "Ответ без запрещенных символов и достаточной длины для прохождения валидации",
            "А" * 2000,  # Максимальная длина
        ],
    )
    def test_validate_answer_text_success(self, valid_answer_text):
        """Тест успешной валидации корректного текста ответа."""
        # Arrange
        validator = UserQuestionValidator()

        # Act & Assert
        # Не должно вызывать исключений
        validator.validate_answer_text(valid_answer_text)

    @pytest.mark.parametrize(
        "invalid_answer_text, expected_error",
        [
            ("Ответ с <script>", "недопустимые символы"),
            ("Ответ с > символом", "недопустимые символы"),
            ("Ответ с & амперсандом", "недопустимые символы"),
            ('Ответ с " кавычками', "недопустимые символы"),
            ("Ответ с ' апострофом", "недопустимые символы"),
            ("Ответ с \\ бэкслешем", "недопустимые символы"),
            ("Ответ с ; точкой с запятой", "недопустимые символы"),
        ],
    )
    def test_validate_answer_text_invalid(self, invalid_answer_text, expected_error):
        """Тест валидации некорректного текста ответа."""
        # Arrange
        validator = UserQuestionValidator()

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validator.validate_answer_text(invalid_answer_text)

        assert expected_error in str(exc_info.value)
