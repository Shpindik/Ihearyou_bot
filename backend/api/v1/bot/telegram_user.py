"""Bot API эндпоинты для работы с пользователями."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.schemas.bot.telegram_user import (
    BotInactiveUserResponse,
    BotReminderStatusResponse,
    TelegramUserRequest,
    TelegramUserResponse,
)
from backend.services.telegram_user import telegram_user_service


router = APIRouter(prefix="/telegram-user", tags=["Bot Telegram User API"])


@router.post(
    "/register",
    response_model=TelegramUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Регистрация пользователя Telegram",
    description="Создает или обновляет пользователя Telegram в системе при получении сообщений от бота",
    responses={
        200: {"description": "Пользователь успешно зарегистрирован или обновлен"},
        400: {"description": "Ошибка валидации данных запроса"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def register_telegram_user(
    request: TelegramUserRequest, db: AsyncSession = Depends(get_session)
) -> TelegramUserResponse:
    """Регистрация пользователя Telegram в системе.

    Автоматически определяет создание нового пользователя или обновление
    существующего на основе telegram_id.
    """
    return await telegram_user_service.register_user(request, db)


@router.get(
    "/inactive-users",
    status_code=status.HTTP_200_OK,
    summary="Получение неактивных пользователей для напоминаний",
    description="Возвращает список неактивных пользователей для отправки автоматических напоминаний",
    responses={
        200: {"description": "Список неактивных пользователей успешно получен"},
        400: {"description": "Ошибка валидации параметров запроса"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_inactive_users_for_reminders(
    inactive_days: int = Query(10, description="Дни неактивности", ge=1),
    days_since_last_reminder: int = Query(10, description="Дни с последнего напоминания", ge=1),
    db: AsyncSession = Depends(get_session),
) -> list[BotInactiveUserResponse]:
    """Получение неактивных пользователей для автоматических напоминаний.

    Возвращает список пользователей, которым нужно отправить напоминания.
    Используется планировщиком задач бота.
    """
    return await telegram_user_service.get_inactive_users(
        db=db, inactive_days=inactive_days, days_since_last_reminder=days_since_last_reminder
    )


@router.post(
    "/update-reminder-status",
    status_code=status.HTTP_200_OK,
    summary="Обновление статуса отправки напоминания",
    description="Обновляет время последней отправки напоминания пользователю",
    responses={
        200: {"description": "Статус успешно обновлен"},
        400: {"description": "Ошибка валидации данных"},
        404: {"description": "Пользователь не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def update_reminder_status(
    telegram_user_id: int = Query(..., description="ID пользователя в Telegram"),
    db: AsyncSession = Depends(get_session),
) -> BotReminderStatusResponse:
    """Обновление времени отправки напоминания пользователю.

    Вызывается ботом после успешной отправки напоминания
    для обновления поля reminder_sent_at.
    """
    return await telegram_user_service.update_reminder_status(db=db, telegram_user_id=telegram_user_id)
