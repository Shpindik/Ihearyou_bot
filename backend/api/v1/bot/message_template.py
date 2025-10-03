"""Bot API эндпоинты для работы с шаблонами напоминаний."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.schemas.bot.message_template import BotMessageTemplateResponse
from backend.services.message_template import message_template_service


router = APIRouter(prefix="/message-template", tags=["Bot Message Template API"])


@router.get(
    "/active-template",
    response_model=BotMessageTemplateResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение активного шаблона для напоминаний",
    description="Возвращает последний созданный активный шаблон для автоматических напоминаний",
    responses={
        200: {"description": "Активный шаблон успешно получен"},
        404: {"description": "Активные шаблоны не найдены"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_active_message_template(
    db: AsyncSession = Depends(get_session),
) -> BotMessageTemplateResponse:
    """Получение активного шаблона для автоматических напоминаний.

    Возвращает самый новый активный шаблон для персонализации сообщений.
    Используется ботом для отправки персонализированных напоминаний пользователям.
    """
    return await message_template_service.get_default_template_response(db=db)
