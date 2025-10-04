"""CRUD операции для вопросов пользователей."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import UserQuestion
from backend.models.enums import QuestionStatus

from .base import BaseCRUD


class QuestionCRUD(BaseCRUD[UserQuestion, dict, dict]):
    """CRUD операции для вопросов пользователей."""

    def __init__(self):
        """Инициализация CRUD для вопросов пользователей."""
        super().__init__(UserQuestion)

    async def create_question(
        self,
        db: AsyncSession,
        telegram_user_id: int,
        question_text: str,
    ) -> UserQuestion:
        """Создать новый вопрос пользователя.

        Args:
            db: Сессия базы данных
            telegram_user_id: ID пользователя в Telegram
            question_text: Текст вопроса

        Returns:
            Созданный вопрос пользователя
        """
        question_data = {
            "telegram_user_id": telegram_user_id,
            "question_text": question_text,
            "status": QuestionStatus.PENDING,
        }

        question = UserQuestion(**question_data)
        db.add(question)
        await db.commit()
        await db.refresh(question)
        return question

    async def answer_question(
        self,
        db: AsyncSession,
        question_id: int,
        answer_text: str,
        admin_user_id: int,
    ) -> UserQuestion:
        """Ответить на вопрос пользователя.

        Args:
            db: Сессия базы данных
            question_id: ID вопроса
            answer_text: Текст ответа
            admin_user_id: ID администратора, отвечающего на вопрос

        Returns:
            Обновленный вопрос с ответом
        """
        question = await self.get(db, id=question_id)
        if question:
            from datetime import datetime, timezone

            question.answer_text = answer_text
            question.status = QuestionStatus.ANSWERED
            question.admin_user_id = admin_user_id
            question.answered_at = datetime.now(timezone.utc)
            db.add(question)
            await db.commit()
            await db.refresh(question)
        return question

    async def get_questions_by_status(
        self,
        db: AsyncSession,
        status: Optional[QuestionStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[UserQuestion]:
        """Получить вопросы по статусу с пагинацией.

        Args:
            db: Сессия базы данных
            status: Фильтр по статусу вопроса
            skip: Количество записей для пропуска
            limit: Максимальное количество записей

        Returns:
            Список вопросов
        """
        query = select(UserQuestion)

        if status is not None:
            query = query.where(UserQuestion.status == status)

        query = query.order_by(UserQuestion.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def count_questions_by_status(
        self,
        db: AsyncSession,
        status: Optional[QuestionStatus] = None,
    ) -> int:
        """Подсчитать количество вопросов по статусу.

        Args:
            db: Сессия базы данных
            status: Фильтр по статусу вопроса

        Returns:
            Количество вопросов
        """
        query = select(func.count(UserQuestion.id))

        if status is not None:
            query = query.where(UserQuestion.status == status)

        result = await db.execute(query)
        return result.scalar() or 0

    async def get_questions_statistics(self, db: AsyncSession) -> dict:
        """Получить общую статистику по вопросам.

        Args:
            db: Сессия базы данных

        Returns:
            Словарь со статистикой вопросов
        """
        total = await self.count_questions_by_status(db)
        pending = await self.count_questions_by_status(db, QuestionStatus.PENDING)
        answered = await self.count_questions_by_status(db, QuestionStatus.ANSWERED)

        return {
            "total": total,
            "pending": pending,
            "answered": answered,
        }


question_crud = QuestionCRUD()
