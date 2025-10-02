"""Административные эндпоинты для шаблонов напоминаний."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.core.dependencies import AdminOnly, ModeratorOrAdmin
from backend.schemas.admin.reminder_template import (
    AdminReminderTemplateCreate,
    AdminReminderTemplateListResponse,
    AdminReminderTemplateResponse,
    AdminReminderTemplateUpdate,
)
from backend.services.reminder_template import reminder_template_service


router = APIRouter(prefix="/admin/reminder-templates", tags=["Admin Reminder Templates"])


@router.get(
    "/",
    response_model=AdminReminderTemplateListResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение списка шаблонов напоминаний (админ)",
    description="Возвращает список всех шаблонов напоминаний с их статистикой использования",
    responses={
        200: {"description": "Список шаблонов успешно получен"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_reminder_templates(
    current_admin: ModeratorOrAdmin,
    db: AsyncSession = Depends(get_session),
) -> AdminReminderTemplateListResponse:
    """Получение списка шаблонов напоминаний.

    Требует авторизации с ролью модератора или администратора.
    Возвращает все шаблоны напоминаний с информацией об использовании.
    """
    return await reminder_template_service.get_admin_templates(db=db)


@router.post(
    "/",
    response_model=AdminReminderTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание шаблона напоминания (админ)",
    description="Создает новый шаблон напоминания для автоматической отправки",
    responses={
        201: {"description": "Шаблон напоминания успешно создан"},
        400: {"description": "Ошибка валидации данных или шаблон с таким именем уже существует"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def create_reminder_template(
    request: AdminReminderTemplateCreate,
    current_admin: AdminOnly,
    db: AsyncSession = Depends(get_session),
) -> AdminReminderTemplateResponse:
    """Создание нового шаблона напоминания.

    Требует авторизации с ролью администратора.
    Создает новый шаблон для автоматической отправки напоминаний пользователям.
    """
    return await reminder_template_service.create_admin_template(db=db, request=request)


@router.put(
    "/{id}",
    response_model=AdminReminderTemplateResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновление шаблона напоминания (админ)",
    description="Обновляет существующий шаблон напоминания",
    responses={
        200: {"description": "Шаблон напоминания успешно обновлен"},
        400: {"description": "Ошибка валидации данных"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Шаблон напоминания не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def update_reminder_template(
    id: int,
    request: AdminReminderTemplateUpdate,
    current_admin: AdminOnly,
    db: AsyncSession = Depends(get_session),
) -> AdminReminderTemplateResponse:
    """Обновление шаблона напоминания.

    Требует авторизации с ролью администратора.
    Обновляет существующий шаблон напоминания с новыми параметрами.
    """
    return await reminder_template_service.update_admin_template(db=db, template_id=id, request=request)


@router.post(
    "/{id}/activate",
    response_model=AdminReminderTemplateResponse,
    status_code=status.HTTP_200_OK,
    summary="Активация шаблона напоминания (админ)",
    description="Активирует шаблон напоминания для использования в автоматических рассылках",
    responses={
        200: {"description": "Шаблон напоминания успешно активирован"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Шаблон напоминания не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def activate_reminder_template(
    id: int,
    current_admin: AdminOnly,
    db: AsyncSession = Depends(get_session),
) -> AdminReminderTemplateResponse:
    """Активация шаблона напоминания.

    Требует авторизации с ролью администратора.
    Активирует шаблон для использования в автоматических напоминаниях.
    """
    return await reminder_template_service.activate_template(db=db, template_id=id)


@router.post(
    "/{id}/deactivate",
    response_model=AdminReminderTemplateResponse,
    status_code=status.HTTP_200_OK,
    summary="Деактивация шаблона напоминания (админ)",
    description="Деактивирует шаблон напоминания",
    responses={
        200: {"description": "Шаблон напоминания успешно деактивирован"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Шаблон напоминания не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def deactivate_reminder_template(
    id: int,
    current_admin: AdminOnly,
    db: AsyncSession = Depends(get_session),
) -> AdminReminderTemplateResponse:
    """Деактивация шаблона напоминания.

    Требует авторизации с ролью администратора.
    Деактивирует шаблон и исключает его из автоматических рассылок.
    """
    return await reminder_template_service.deactivate_template(db=db, template_id=id)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление шаблона напоминания (админ)",
    description="Удаляет шаблон напоминания из системы (только если не используется)",
    responses={
        204: {"description": "Шаблон напоминания успешно удален"},
        400: {"description": "Нельзя удалить используемый шаблон"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Шаблон напоминания не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def delete_reminder_template(id: int, current_admin: AdminOnly, db: AsyncSession = Depends(get_session)) -> None:
    """Удаление шаблона напоминания.

    Требует авторизации с ролью администратора.
    Удаляет шаблон, только если он не используется в уведомлениях.
    """
    await reminder_template_service.delete_template(db=db, template_id=id)
