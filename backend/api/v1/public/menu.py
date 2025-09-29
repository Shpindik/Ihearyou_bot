"""Публичные эндпоинты для работы с меню."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.crud import activity_crud, menu_crud, user_crud
from backend.models.enums import AccessLevel, ActivityType
from backend.schemas.public.menu import MenuContentResponse, MenuItemListResponse


router = APIRouter(prefix="/menu-items", tags=["Public Menu"])


@router.get("/", response_model=MenuItemListResponse, status_code=status.HTTP_200_OK)
async def get_menu_items(
    telegram_user_id: int = Query(..., description="ID пользователя в Telegram"),
    parent_id: int = Query(
        None, description="ID родительского пункта меню (null для корневого уровня)"
    ),
    include_children: bool = Query(
        False, description="Включить дочерние элементы в ответ"
    ),
    db: AsyncSession = Depends(get_session),
) -> MenuItemListResponse:
    """Получение структуры меню для пользователя.

    GET /api/v1/menu-items
    Параметры:
    - telegram_user_id (int, обязательный) - ID пользователя в Telegram
    - parent_id (int, необязательный) - ID родительского пункта меню
    """
    # Получаем или создаем пользователя
    user = await user_crud.get_by_telegram_id(db, telegram_user_id)
    if not user:
        # Создаем пользователя автоматически
        user = await user_crud.get_or_create(
            db=db,
            telegram_id=telegram_user_id,
            first_name="Пользователь",
            last_name=None,
            username=None,
        )

    # Определяем уровень доступа пользователя (пока не используется)
    # access_level = AccessLevel.PREMIUM if user.subscription_type == "premium" else AccessLevel.FREE

    # Получаем пункты меню (простая загрузка без children)
    items = await menu_crud.get_by_parent_id(db, parent_id, True)

    # Преобразуем в словари для избежания проблем с lazy loading
    items_data = []
    for item in items:
        children_data = []

        # Загружаем дочерние элементы только если запрошено
        if include_children:
            children = await menu_crud.get_by_parent_id(db, item.id, True)
            for child in children:
                child_dict = {
                    "id": child.id,
                    "title": child.title,
                    "description": child.description,
                    "parent_id": child.parent_id,
                    "bot_message": child.bot_message,
                    "is_active": child.is_active,
                    "access_level": child.access_level,
                    "children": [],  # Пустой список для избежания lazy loading
                }
                children_data.append(child_dict)

        item_dict = {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "parent_id": item.parent_id,
            "bot_message": item.bot_message,
            "is_active": item.is_active,
            "access_level": item.access_level,
            "children": children_data,
        }
        items_data.append(item_dict)

    return MenuItemListResponse(items=items_data)


@router.get(
    "/{id}/content", response_model=MenuContentResponse, status_code=status.HTTP_200_OK
)
async def get_menu_item_content(
    id: int,
    telegram_user_id: int = Query(..., description="ID пользователя в Telegram"),
    db: AsyncSession = Depends(get_session),
) -> MenuContentResponse:
    """Получение контента конкретного пункта меню.

    GET /api/v1/menu-items/{id}/content
    Параметры:
    - telegram_user_id (int, обязательный) - ID пользователя в Telegram
    """
    # Получаем пользователя
    user = await user_crud.get_by_telegram_id(db, telegram_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Получаем пункт меню с контентом
    menu_item = await menu_crud.get_with_content(db, id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    # Получаем дочерние элементы
    children = await menu_crud.get_by_parent_id(db, id, True)

    # Преобразуем children в словари для избежания проблем с lazy loading
    children_data = []
    for child in children:
        child_dict = {
            "id": child.id,
            "title": child.title,
            "description": child.description,
            "parent_id": child.parent_id,
            "bot_message": child.bot_message,
            "is_active": child.is_active,
            "access_level": child.access_level,
            "children": [],  # Пустой список для избежания lazy loading
        }
        children_data.append(child_dict)

    # Проверяем доступ
    access_level = (
        AccessLevel.PREMIUM if user.subscription_type == "premium" else AccessLevel.FREE
    )
    if (
        menu_item.access_level == AccessLevel.PREMIUM
        and access_level != AccessLevel.PREMIUM
    ):
        raise HTTPException(status_code=403, detail="Premium content access required")

    # Записываем активность
    await activity_crud.create_activity(
        db=db,
        telegram_user_id=user.id,
        menu_item_id=id,
        activity_type=ActivityType.NAVIGATION,
    )

    # Увеличиваем счетчик просмотров
    await menu_crud.increment_view_count(db, id)

    return MenuContentResponse(
        id=menu_item.id,
        title=menu_item.title,
        description=menu_item.description,
        bot_message=menu_item.bot_message,
        content_files=menu_item.content_files,
        children=children_data,
    )
