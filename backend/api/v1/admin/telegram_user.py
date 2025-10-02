"""Административные эндпоинты для управления пользователями Telegram."""

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.core.dependencies import CurrentAdmin
from backend.schemas.admin.telegram_user import AdminTelegramUserListResponse, AdminTelegramUserResponse
from backend.services.telegram_user import telegram_user_service


router = APIRouter(prefix="/admin/telegram-users", tags=["Admin Telegram Users"])


@router.get(
    "/",
    response_model=AdminTelegramUserListResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение списка пользователей Telegram (админ)",
    description="Возвращает список всех зарегистрированных пользователей Telegram для администраторов",
    responses={
        200: {"description": "Список пользователей успешно получен"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_telegram_users(
    admin: CurrentAdmin,
    db: AsyncSession = Depends(get_session),
) -> AdminTelegramUserListResponse:
    """Получение списка всех пользователей Telegram для администраторов.

    Требует авторизации администратора через JWT токен.
    MVP версия - возвращает всех пользователей без пагинации и фильтрации.
    Включает базовую статистику по активностям и вопросам.
    """
    return await telegram_user_service.get_all_users(db)


@router.get(
    "/{user_id}",
    response_model=AdminTelegramUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение информации о пользователе (админ)",
    description="Возвращает детальную информацию о конкретном пользователе Telegram с полной статистикой",
    responses={
        200: {"description": "Информация о пользователе успешно получена"},
        400: {"description": "Ошибка валидации параметров запроса"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Пользователь не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_telegram_user(
    admin: CurrentAdmin,
    user_id: int = Path(ge=1, description="ID пользователя в системе"),
    db: AsyncSession = Depends(get_session),
) -> AdminTelegramUserResponse:
    """Получение детальной информации о конкретном пользователе Telegram.

    Требует авторизации администратора через JWT токен.
    Возвращает полную информацию о пользователе включая:
    - Базовые данные (ID, имя, username, подписка)
    - Активность (последняя активность, напоминания)
    - Статистику (количество активностей и вопросов)
    - Временные метки (создание, обновление)
    """
    return await telegram_user_service.get_user_by_id(user_id, db)
