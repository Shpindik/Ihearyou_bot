"""Административные эндпоинты для управления меню."""

from fastapi import APIRouter, Depends, Query, status
from fastapi.security import HTTPBearer

from backend.schemas.admin.menu import (
    AdminContentFileCreate,
    AdminContentFileResponse,
    AdminContentFileUpdate,
    AdminMenuItemCreate,
    AdminMenuItemListResponse,
    AdminMenuItemResponse,
    AdminMenuItemUpdate,
)


router = APIRouter(prefix="/admin/menu-items", tags=["Admin Menu"])
security = HTTPBearer()


@router.get(
    "/", response_model=AdminMenuItemListResponse, status_code=status.HTTP_200_OK
)
async def get_admin_menu_items(
    page: int = Query(1, description="Номер страницы (по умолчанию 1)"),
    limit: int = Query(
        20, description="Количество записей на странице (по умолчанию 20)"
    ),
    parent_id: int = Query(None, description="Фильтр по родительскому пункту"),
    is_active: bool = Query(None, description="Фильтр по активности"),
    access_level: str = Query(
        None, description="Фильтр по уровню доступа (free, premium)"
    ),
    token: str = Depends(security),
) -> AdminMenuItemListResponse:
    """Получение списка пунктов меню.

    GET /api/v1/admin/menu-items
    Требует: Authorization: Bearer <token>
    """
    pass


@router.post(
    "/", response_model=AdminMenuItemResponse, status_code=status.HTTP_201_CREATED
)
async def create_menu_item(
    request: AdminMenuItemCreate, token: str = Depends(security)
) -> AdminMenuItemResponse:
    """Создание нового пункта меню.

    POST /api/v1/admin/menu-items
    Требует: Authorization: Bearer <token>
    """
    pass


@router.put(
    "/{id}", response_model=AdminMenuItemResponse, status_code=status.HTTP_200_OK
)
async def update_menu_item(
    id: int, request: AdminMenuItemUpdate, token: str = Depends(security)
) -> AdminMenuItemResponse:
    """Обновление пункта меню.

    PUT /api/v1/admin/menu-items/{id}
    Требует: Authorization: Bearer <token>
    """
    pass


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(id: int, token: str = Depends(security)) -> None:
    """Удаление пункта меню.

    DELETE /api/v1/admin/menu-items/{id}
    Требует: Authorization: Bearer <token>
    """
    pass


@router.get(
    "/{id}/content-files",
    response_model=list[AdminContentFileResponse],
    status_code=status.HTTP_200_OK,
)
async def get_content_files(
    id: int, token: str = Depends(security)
) -> list[AdminContentFileResponse]:
    """Получение файлов контента для пункта меню.

    GET /api/v1/admin/menu-items/{id}/content-files
    Требует: Authorization: Bearer <token>
    """
    pass


@router.post(
    "/{id}/content-files",
    response_model=AdminContentFileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_content_file(
    id: int, request: AdminContentFileCreate, token: str = Depends(security)
) -> AdminContentFileResponse:
    """Добавление файла контента к пункту меню.

    POST /api/v1/admin/menu-items/{id}/content-files
    Требует: Authorization: Bearer <token>
    """
    pass


@router.put(
    "/content-files/{file_id}",
    response_model=AdminContentFileResponse,
    status_code=status.HTTP_200_OK,
)
async def update_content_file(
    file_id: int, request: AdminContentFileUpdate, token: str = Depends(security)
) -> AdminContentFileResponse:
    """Обновление файла контента.

    PUT /api/v1/admin/content-files/{id}
    Требует: Authorization: Bearer <token>
    """
    pass


@router.delete("/content-files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content_file(file_id: int, token: str = Depends(security)) -> None:
    """Удаление файла контента.

    DELETE /api/v1/admin/content-files/{id}
    Требует: Authorization: Bearer <token>
    """
    pass
