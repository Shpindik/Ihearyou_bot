"""Эндпойнты для обработки webhook от Telegram."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.crud import user_crud
from backend.schemas.webhook import TelegramWebhookRequest, TelegramWebhookResponse


router = APIRouter(prefix="/webhook", tags=["Webhook"])


@router.post(
    "/telegram", response_model=TelegramWebhookResponse, status_code=status.HTTP_200_OK
)
async def handle_telegram_webhook(
    request: TelegramWebhookRequest, db: AsyncSession = Depends(get_session)
) -> TelegramWebhookResponse:
    """Обработка webhook от Telegram для автоматического управления пользователями.

    POST /api/v1/webhook/telegram
    Автоматически создает/обновляет пользователей при получении сообщений
    """
    # Извлекаем данные пользователя из webhook
    user_data = request.message["from"]

    # Создаем или обновляем пользователя
    user = await user_crud.get_or_create(
        db=db,
        telegram_id=user_data["id"],
        first_name=user_data["first_name"],
        last_name=user_data.get("last_name"),
        username=user_data.get("username"),
    )

    return TelegramWebhookResponse(
        user={
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "subscription_type": user.subscription_type,
            "last_activity": user.last_activity.isoformat()
            if user.last_activity
            else None,
            "reminder_sent_at": user.reminder_sent_at.isoformat()
            if user.reminder_sent_at
            else None,
            "created_at": user.created_at.isoformat(),
        },
        message_processed=True,
        user_created=user.id is not None,
        user_updated=True,
    )


@router.get("/telegram/health", status_code=status.HTTP_200_OK)
async def webhook_health_check():
    """Проверка работоспособности webhook эндпоинта.

    GET /api/v1/webhook/telegram/health
    """
    return {"status": "ok", "message": "Webhook endpoint is healthy"}
