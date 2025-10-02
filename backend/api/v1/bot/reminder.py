"""Bot API эндпоинты для работы с напоминаниями."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.core.exceptions import IHearYouException, NotFoundError, ValidationError
from backend.schemas.bot.reminder import InactiveListUserResponse
from backend.schemas.bot.reminder_template import BotReminderTemplateResponse
from backend.services.reminder import reminder_service
from backend.services.reminder_template import reminder_template_service


router = APIRouter(prefix="/reminders", tags=["Bot Telegram User API"])


@router.get(
    "/inactive_users",
    response_model=InactiveListUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение неактивных пользователей",
    description="Получение списка неактивных пользователей",
    responses={
        200: {"description": "Пользователь успешно зарегистрирован или обновлен"},
        400: {"description": "Ошибка валидации параметров запроса"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_inactive_users(
    inactive_days: int = Query(..., gt=0, description="Количество неактивных дней"),
    db: AsyncSession = Depends(get_session),
) -> InactiveListUserResponse:
    """Получение списка пользователей неактивных заданное количество дней.

    GET /api/v1/bot/reminders/inactive_users
    """
    try:
        result = await reminder_service.get_inactive_users(inactive_days=inactive_days, db=db)
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IHearYouException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/template",
    response_model=BotReminderTemplateResponse | dict,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Шаблоно успешно получен"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_reminder_templates(
    db: AsyncSession = Depends(get_session),
) -> BotReminderTemplateResponse | dict:
    """Получить последний активный шаблон.

    GET /api/v1/bot/reminders/template
    """
    try:
        return await reminder_template_service.get_last_active_template(db=db)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IHearYouException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
