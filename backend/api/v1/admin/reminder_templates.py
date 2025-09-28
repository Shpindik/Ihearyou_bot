"""Административные эндпоинты для шаблонов напоминаний."""

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from schemas.admin.reminder_templates import (
    AdminReminderTemplateResponse,
    AdminReminderTemplateListResponse,
    AdminReminderTemplateCreate,
    AdminReminderTemplateUpdate,
)

router = APIRouter(prefix="/admin/reminder-templates", tags=["Admin Reminder Templates"])
security = HTTPBearer()


@router.get("/", response_model=AdminReminderTemplateListResponse, status_code=status.HTTP_200_OK)
async def get_reminder_templates(
    token: str = Depends(security)
) -> AdminReminderTemplateListResponse:
    """
    Получение шаблонов напоминаний.
    
    GET /api/v1/admin/reminder-templates
    Требует: Authorization: Bearer <token>
    """
    pass


@router.post("/", response_model=AdminReminderTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder_template(
    request: AdminReminderTemplateCreate,
    token: str = Depends(security)
) -> AdminReminderTemplateResponse:
    """
    Создание шаблона напоминания.
    
    POST /api/v1/admin/reminder-templates
    Требует: Authorization: Bearer <token>
    """
    pass


@router.put("/{id}", response_model=AdminReminderTemplateResponse, status_code=status.HTTP_200_OK)
async def update_reminder_template(
    id: int,
    request: AdminReminderTemplateUpdate,
    token: str = Depends(security)
) -> AdminReminderTemplateResponse:
    """
    Обновление шаблона напоминания.
    
    PUT /api/v1/admin/reminder-templates/{id}
    Требует: Authorization: Bearer <token>
    """
    pass


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder_template(
    id: int,
    token: str = Depends(security)
) -> None:
    """
    Удаление шаблона напоминания.
    
    DELETE /api/v1/admin/reminder-templates/{id}
    Требует: Authorization: Bearer <token>
    """
    pass
