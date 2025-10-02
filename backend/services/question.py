"""Сервис для работы с вопросами пользователей."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.question import question_crud
from backend.crud.telegram_user import telegram_user_crud
from backend.schemas.admin.question import AdminQuestionAnswer, AdminQuestionListResponse, AdminQuestionResponse
from backend.schemas.public.question import UserQuestionCreate, UserQuestionResponse
from backend.validators.question import user_question_validator


class UserQuestionService:
    """Сервис для работы с вопросами пользователей."""

    def __init__(self):
        """Инициализация сервиса User Question."""
        self.question_crud = question_crud
        self.telegram_user_crud = telegram_user_crud
        self.validator = user_question_validator

    async def create_user_question(self, request: UserQuestionCreate, db: AsyncSession) -> UserQuestionResponse:
        """Создание нового вопроса пользователем.

        Args:
            request: Данные для создания вопроса
            db: Сессия базы данных

        Returns:
            Ответ с данными созданного вопроса
        """
        user = await self.telegram_user_crud.get_by_telegram_id(db, request.telegram_user_id)
        self.validator.validate_user_exists(user)

        self.validator.validate_question_text(request.question_text)

        question = await self.question_crud.create_question(
            db=db,
            telegram_user_id=user.id,
            question_text=request.question_text,
        )

        # Обновляем счетчик вопросов у пользователя
        await self.telegram_user_crud.update_questions_count(db, user.id)

        return UserQuestionResponse(
            question_text=question.question_text,
            status=question.status,
        )

    async def get_admin_questions(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        status: str = None,
    ) -> AdminQuestionListResponse:
        """Получение списка вопросов для администраторов.

        Args:
            db: Сессия базы данных
            page: Номер страницы
            limit: Количество записей на странице
            status: Фильтр по статусу

        Returns:
            Список вопросов с пагинацией
        """
        skip = (page - 1) * limit

        questions = await self.question_crud.get_questions_by_status(db=db, status=status, skip=skip, limit=limit)

        total = await self.question_crud.count_questions_by_status(db=db, status=status)
        pages = (total + limit - 1) // limit

        items = [
            AdminQuestionResponse(
                id=question.id,
                telegram_user_id=question.telegram_user_id,
                question_text=question.question_text,
                answer_text=question.answer_text,
                status=question.status,
                created_at=question.created_at,
                answered_at=question.answered_at,
            )
            for question in questions
        ]

        return AdminQuestionListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )

    async def answer_question(
        self, db: AsyncSession, question_id: int, request: AdminQuestionAnswer, admin_user_id: int
    ) -> AdminQuestionResponse:
        """Ответ администратора на вопрос пользователя.

        Args:
            db: Сессия базы данных
            question_id: ID вопроса
            request: Данные ответа
            admin_user_id: ID администратора

        Returns:
            Ответ с обновленным вопросом
        """
        question = await self.question_crud.get(db, question_id)
        self.validator.validate_question_exists(question)

        self.validator.validate_answer_text(request.answer_text)

        updated_question = await self.question_crud.answer_question(
            db=db,
            question_id=question_id,
            answer_text=request.answer_text,
            admin_user_id=admin_user_id,
        )

        return AdminQuestionResponse(
            id=updated_question.id,
            telegram_user_id=updated_question.telegram_user_id,
            question_text=updated_question.question_text,
            answer_text=updated_question.answer_text,
            status=updated_question.status,
            created_at=updated_question.created_at,
            answered_at=updated_question.answered_at,
        )

    async def get_questions_statistics(self, db: AsyncSession) -> dict:
        """Получение статистики по вопросам для аналитики.

        Args:
            db: Сессия базы данных

        Returns:
            Статистика по вопросам
        """
        return await self.question_crud.get_questions_statistics(db=db)


user_question_service = UserQuestionService()
