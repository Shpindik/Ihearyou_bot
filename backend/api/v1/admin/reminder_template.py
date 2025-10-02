"""Административные эндпоинты для шаблонов напоминаний."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.core.exceptions import IHearYouException, NotFoundError, ValidationError
from backend.schemas.admin.reminder_template import (
    AdminReminderTemplateCreate,
    AdminReminderTemplateListResponse,
    AdminReminderTemplateResponse,
    AdminReminderTemplateUpdate,
)
from backend.services.reminder_template import reminder_template_service


router = APIRouter(prefix="/admin/reminder-templates", tags=["Admin Reminder Templates"])
security = HTTPBearer()


@router.get(
    "/",
    response_model=AdminReminderTemplateListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Список шаблонов успешно получен"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_reminder_templates(
    db: AsyncSession = Depends(get_session),
    # token: str = Depends(security),
) -> AdminReminderTemplateListResponse:
    """Получение шаблонов напоминаний.

    GET /api/v1/admin/reminder-templates
    Требует: Authorization: Bearer <token>
    """
    try:
        return await reminder_template_service.get_reminder_templates(db=db)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IHearYouException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/",
    response_model=AdminReminderTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Шаблон успешно создан"},
        400: {"description": "Ошибка валидации параметров запроса"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def create_reminder_template(
    request: AdminReminderTemplateCreate,
    db: AsyncSession = Depends(get_session),
    # token: str = Depends(security),
) -> AdminReminderTemplateResponse:
    """Создание шаблона напоминания.

    POST /api/v1/admin/reminder-templates
    Требует: Authorization: Bearer <token>
    """
    try:
        return await reminder_template_service.create_reminder_template(request=request, db=db)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IHearYouException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put(
    "/{id}",
    response_model=AdminReminderTemplateResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Шаблон успешно создан"},
        400: {"description": "Ошибка валидации параметров запроса"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def update_reminder_template(
    id: int,
    request: AdminReminderTemplateUpdate,
    db: AsyncSession = Depends(get_session),
    # token: str = Depends(security),
) -> AdminReminderTemplateResponse:
    """Обновление шаблона напоминания.

    PUT /api/v1/admin/reminder-templates/{id}
    Требует: Authorization: Bearer <token>
    """
    try:
        return await reminder_template_service.update_reminder_template(template_id=id, request=request, db=db)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IHearYouException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Шаблон успешно удален"},
        400: {"description": "Ошибка валидации параметров запроса"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def delete_reminder_template(
    id: int,
    db: AsyncSession = Depends(get_session),  # token: str = Depends(security)
) -> None:
    """Удаление шаблона напоминания.

    DELETE /api/v1/admin/reminder-templates/{id}
    Требует: Authorization: Bearer <token>
    """
    try:
        return await reminder_template_service.delete_reminder_template(template_id=id, db=db)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IHearYouException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
