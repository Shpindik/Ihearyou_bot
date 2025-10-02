"""Bot API эндпоинты для работы с пользователями."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.core.exceptions import ValidationError
from backend.crud import telegram_user_crud
from backend.schemas.bot.telegram_user import TelegramUserRequest, TelegramUserResponse
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
    try:
        return await telegram_user_service.register_user(request, db)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Отсутствует обязательное поле в запросе: {str(e)}"
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка базы данных при регистрации пользователя"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера")


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
    days_since_last_reminder: int = Query(7, description="Дни с последнего напоминания", ge=0),
    db: AsyncSession = Depends(get_session),
) -> list[dict[str, str | int | None]]:
    """Получение неактивных пользователей для автоматических напоминаний.

    Возвращает список пользователей, которым нужно отправить напоминания.
    Используется планировщиком задач бота.
    """
    try:
        inactive_users = await telegram_user_crud.get_inactive_users(
            db=db, inactive_days=inactive_days, days_since_last_reminder=days_since_last_reminder
        )

        return [
            {
                "telegram_user_id": user.telegram_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "last_activity": user.last_activity.isoformat() if user.last_activity else None,
                "reminder_sent_at": user.reminder_sent_at.isoformat() if user.reminder_sent_at else None,
            }
            for user in inactive_users
        ]

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка базы данных при получении неактивных пользователей",
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера")


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
    telegram_user_id: int,
    db: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """Обновление времени отправки напоминания пользователю.

    Вызывается ботом после успешной отправки напоминания
    для обновления поля reminder_sent_at.
    """
    try:
        user = await telegram_user_crud.get_by_telegram_id(db, telegram_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Пользователь с telegram_id {telegram_user_id} не найден"
            )

        await telegram_user_crud.update_reminder_sent_status(db, user.id)

        return {
            "success": "true",
            "message": f"Статус напоминания обновлен для пользователя {user.first_name}",
            "reminder_sent_at": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка базы данных при обновлении статуса"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера")
