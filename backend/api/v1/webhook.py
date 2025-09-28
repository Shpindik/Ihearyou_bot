"""Эндпойнты для обработки webhook от Telegram."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_session
from crud import user_crud
from schemas.webhook import (
    TelegramWebhookRequest,
    TelegramWebhookResponse,
)

router = APIRouter(prefix="/webhook", tags=["Webhook"])


@router.post("/telegram", response_model=TelegramWebhookResponse, status_code=status.HTTP_200_OK)
async def handle_telegram_webhook(
    request: TelegramWebhookRequest,
    db: AsyncSession = Depends(get_session)
) -> TelegramWebhookResponse:
    """
    Обработка webhook от Telegram для автоматического управления пользователями.
    
    POST /api/v1/webhook/telegram
    Автоматически создает/обновляет пользователей при получении сообщений
    """
    # Извлекаем данные пользователя из webhook
    user_data = request.message.from_user
    
    # Создаем или обновляем пользователя
    user = await user_crud.get_or_create(
        db=db,
        telegram_id=user_data.id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        username=user_data.username
    )
    
    return TelegramWebhookResponse(
        status="ok",
        user_created=user.id is not None,
        user_updated=True
    )


@router.get("/telegram/health", status_code=status.HTTP_200_OK)
async def webhook_health_check():
    """
    Проверка работоспособности webhook эндпоинта.
    
    GET /api/v1/webhook/telegram/health
    """
    return {"status": "ok", "message": "Webhook endpoint is healthy"}
