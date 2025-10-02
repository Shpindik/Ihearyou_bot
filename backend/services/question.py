"""Сервис для работы с вопросами пользователей."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import asc, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import AdminUser, TelegramUser, UserQuestion
from backend.core.exceptions import ValidationError
from backend.models.enums import QuestionStatus
from backend.schemas.admin.question import (
    AdminQuestionAnswer,
    AdminQuestionListResponse,
    AdminQuestionResponse,
)
from backend.schemas.public.user_question import (
    UserQuestionCreate,
    UserQuestionResponse,
)


class UserQuestionService:
    """Сервис для работы с вопросами пользователей."""

    async def _get_user_by_telegram_id(self, db: AsyncSession, telegram_user_id: int) -> Optional[TelegramUser]:
        result = await db.execute(
            select(TelegramUser).where(TelegramUser.telegram_id == telegram_user_id)
        )
        return result.scalar_one_or_none()

    async def create_question(self, request: UserQuestionCreate, db: AsyncSession) -> UserQuestionResponse:
        user = await self._get_user_by_telegram_id(db, request.telegram_user_id)
        if not user:
            raise ValidationError("Пользователь не найден. Зарегистрируйтесь через бота.")

        question = UserQuestion(
            telegram_user_id=user.id,
            question_text=request.question_text,
            status=QuestionStatus.PENDING,
        )
        db.add(question)
        await db.commit()
        await db.refresh(question)
        return UserQuestionResponse.model_validate(question)

    async def list_questions(
        self, db: AsyncSession, page: int, limit: int, status: Optional[str]
    ) -> AdminQuestionListResponse:
        query = select(UserQuestion)
        count_query = select(func.count(UserQuestion.id))

        if status in {QuestionStatus.PENDING, QuestionStatus.ANSWERED}:
            query = query.where(UserQuestion.status == status)
            count_query = count_query.where(UserQuestion.status == status)

        total = (await db.execute(count_query)).scalar_one()
        pages = max((total + limit - 1) // limit, 1)
        offset = (page - 1) * limit

        query = query.order_by(desc(UserQuestion.created_at)).offset(offset).limit(limit)
        items = (await db.execute(query)).scalars().all()

        return AdminQuestionListResponse(
            items=[AdminQuestionResponse.model_validate(i) for i in items],
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )

    async def answer_question(
        self, db: AsyncSession, id: int, request: AdminQuestionAnswer, admin_user_id: Optional[int] = None
    ) -> AdminQuestionResponse:
        result = await db.execute(select(UserQuestion).where(UserQuestion.id == id))
        question = result.scalar_one_or_none()
        if not question:
            raise ValidationError("Вопрос не найден")

        question.answer_text = request.answer_text
        question.status = QuestionStatus.ANSWERED
        question.answered_at = datetime.now(timezone.utc)
        if admin_user_id:
            question.admin_user_id = admin_user_id

        await db.commit()
        await db.refresh(question)
        return AdminQuestionResponse.model_validate(question)


user_question_service = UserQuestionService()
