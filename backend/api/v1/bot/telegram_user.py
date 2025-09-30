"""Bot API эндпоинты для работы с пользователями."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.core.exceptions import ValidationError
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
